import base64
import datetime
import json
import os
import random
from zoneinfo import ZoneInfo

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google import genai
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.memory import VertexAiMemoryBankService
from google.adk.models import Gemini
from google.adk.tools import ToolContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.cloud import firestore, storage
from google.genai import types

from app.a2ui_utils import a2ui_callback

# Hardcode project ID & GCS bucket name as requested to ensure consistency across environments
PROJECT_ID = "qwiklabs-gcp-02-26648d09f310"
BUCKET_NAME = "it-helpdesk-assets-qwiklabs-gcp-02-26648d09f310"

db = firestore.Client(project=PROJECT_ID)
storage_client = storage.Client(project=PROJECT_ID)


async def generate_memories_callback(callback_context: CallbackContext):
    """WRITE: After each turn, send the session to Memory Bank for extraction if memory service is available."""
    try:
        await callback_context.add_session_to_memory()
    except (ValueError, Exception):
        pass
    return None


async def generate_setup_guide_image(topic: str, tool_context: ToolContext) -> str:
    """Generates an IT technical setup or troubleshooting diagram, saves it as an artifact, and uploads to public Cloud Storage.

    Args:
        topic: Technical topic or setup diagram request (e.g. 'Laptop dock cabling' or 'Router setup').
        tool_context: ADK ToolContext injected automatically.

    Returns:
        The public HTTPS URL of the generated image hosted on Cloud Storage.
    """
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    prompt = f"A clean technical diagram illustrating IT setup and hardware troubleshooting steps for: {topic}"

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        ),
    )

    image_bytes = None
    mime_type = "image/jpeg"
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.inline_data:
                image_bytes = part.inline_data.data
                if part.inline_data.mime_type:
                    mime_type = part.inline_data.mime_type
                break

    if not image_bytes:
        return f"Failed to generate image for topic: {topic}"

    # 1. Save artifact so it appears in Playground's Artifacts panel
    filename = f"guide_{random.randint(1000, 9999)}.jpg"
    artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    await tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # 2. Upload image bytes directly to GCS without writing to a local file
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    return f"Generated setup guide image for '{topic}'. Public URL: {public_url}"


async def generate_hardware_video(topic: str, tool_context: ToolContext) -> str:
    """Generates a short technical demonstration or setup video for an IT hardware topic using gemini-omni-flash-preview in the global region.
    Saves the video as an artifact and uploads its bytes to public Cloud Storage.

    Args:
        topic: IT hardware or setup topic (e.g. 'Laptop unboxing', 'Dual monitor setup', 'Docking station cabling').
        tool_context: ADK ToolContext injected automatically.

    Returns:
        The public HTTPS URL of the generated video hosted on Cloud Storage.
    """
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    prompt = f"A short video demonstrating IT hardware setup, configuration, or troubleshooting for: {topic}"

    interaction = client.interactions.create(
        model="gemini-omni-flash-preview",
        input=prompt,
    )

    video_bytes = None
    mime_type = "video/mp4"

    if hasattr(interaction, "output_video") and interaction.output_video:
        if hasattr(interaction.output_video, "data") and interaction.output_video.data:
            data = interaction.output_video.data
            video_bytes = base64.b64decode(data) if isinstance(data, str) else data
        elif hasattr(interaction.output_video, "bytes") and interaction.output_video.bytes:
            video_bytes = interaction.output_video.bytes

    if not video_bytes and hasattr(interaction, "outputs"):
        for out in getattr(interaction, "outputs", []):
            if hasattr(out, "video") and out.video:
                if hasattr(out.video, "data"):
                    video_bytes = base64.b64decode(out.video.data) if isinstance(out.video.data, str) else out.video.data
                    break

    if not video_bytes:
        return f"Failed to generate video for topic: {topic}"

    filename = f"video_{random.randint(1000, 9999)}.mp4"

    # 1. Save artifact so it shows up in Playground's Artifacts panel
    artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
    await tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # 2. Upload video bytes to public Cloud Storage bucket without writing to local file
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(video_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    return f"Generated video for '{topic}'. Public URL: {public_url}"


def get_ticket_status(ticket_id: str) -> str:
    """Retrieves the details and status of an IT support ticket from Firestore.

    Args:
        ticket_id: The ID of the support ticket (e.g., 'TCK-1001').

    Returns:
        A summary of the ticket details and current status.
    """
    doc = db.collection("tickets").document(ticket_id.upper()).get()
    if not doc.exists:
        return f"Ticket {ticket_id} was not found in the system."
    data = doc.to_dict()
    return (
        f"Ticket ID: {data.get('ticket_id')}\n"
        f"Employee: {data.get('employee_name')}\n"
        f"Issue: {data.get('issue_title')}\n"
        f"Category: {data.get('category')}\n"
        f"Priority: {data.get('priority')}\n"
        f"Status: {data.get('status')}\n"
        f"Description: {data.get('description')}\n"
        f"Created At: {data.get('created_at')}"
    )


def create_ticket(
    employee_name: str,
    issue_title: str,
    category: str = "Hardware",
    priority: str = "Medium",
    description: str = "",
) -> str:
    """Creates a new IT support ticket in Firestore.

    Args:
        employee_name: Name of the employee reporting the issue.
        issue_title: Short title of the problem.
        category: Category of issue (e.g. 'Hardware', 'Software', 'Network').
        priority: Issue priority ('Low', 'Medium', 'High', 'Urgent').
        description: Detailed explanation of the issue.

    Returns:
        Confirmation message with the new ticket ID.
    """
    ticket_num = random.randint(1004, 9999)
    ticket_id = f"TCK-{ticket_num}"
    new_ticket = {
        "ticket_id": ticket_id,
        "employee_name": employee_name,
        "issue_title": issue_title,
        "category": category,
        "priority": priority,
        "status": "Open",
        "description": description,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    db.collection("tickets").document(ticket_id).set(new_ticket)
    return f"Successfully created support ticket {ticket_id} for {employee_name}."


def list_user_tickets(employee_name: str) -> str:
    """Lists all support tickets submitted by a specific employee.

    Args:
        employee_name: Name of the employee.

    Returns:
        A list of support tickets associated with the employee.
    """
    docs = db.collection("tickets").where("employee_name", "==", employee_name).stream()
    tickets = [doc.to_dict() for doc in docs]
    if not tickets:
        return f"No support tickets found for employee '{employee_name}'."
    
    output = [f"Found {len(tickets)} ticket(s) for {employee_name}:"]
    for t in tickets:
        output.append(
            f"- [{t.get('ticket_id')}] {t.get('issue_title')} | Priority: {t.get('priority')} | Status: {t.get('status')}"
        )
    return "\n".join(output)


def get_hardware_info(asset_id_or_user: str) -> str:
    """Retrieves assigned hardware details by asset ID or employee name.

    Args:
        asset_id_or_user: Asset ID (e.g., 'HW-8801') or Employee Name (e.g., 'Alice Smith').

    Returns:
        Hardware specifications and assignment status.
    """
    if asset_id_or_user.upper().startswith("HW-"):
        doc = db.collection("hardware").document(asset_id_or_user.upper()).get()
        if not doc.exists:
            return f"Hardware asset {asset_id_or_user} not found."
        data = doc.to_dict()
        return (
            f"Asset ID: {data.get('asset_id')}\n"
            f"Device: {data.get('device_name')}\n"
            f"Assigned To: {data.get('assigned_to')}\n"
            f"Status: {data.get('status')}\n"
            f"Serial Number: {data.get('serial_number')}"
        )
    else:
        docs = db.collection("hardware").where("assigned_to", "==", asset_id_or_user).stream()
        items = [doc.to_dict() for doc in docs]
        if not items:
            return f"No hardware assigned to employee '{asset_id_or_user}'."
        output = [f"Hardware assigned to {asset_id_or_user}:"]
        for item in items:
            output.append(f"- [{item.get('asset_id')}] {item.get('device_name')} (Status: {item.get('status')}, S/N: {item.get('serial_number')})")
        return "\n".join(output)


def update_ticket_status(
    ticket_id: str,
    new_status: str,
    resolution_notes: str = "",
) -> str:
    """Updates the status and optional resolution notes for an existing ticket in Firestore.

    Args:
        ticket_id: The ID of the support ticket (e.g., 'TCK-1001').
        new_status: The new status ('In Progress', 'Resolved', 'Closed', 'Escalated').
        resolution_notes: Optional notes explaining the resolution or status update.

    Returns:
        Confirmation message of the ticket update.
    """
    doc_ref = db.collection("tickets").document(ticket_id.upper())
    if not doc_ref.get().exists:
        return f"Ticket {ticket_id} was not found."

    update_data = {"status": new_status}
    if resolution_notes:
        update_data["resolution_notes"] = resolution_notes

    doc_ref.update(update_data)
    return f"Successfully updated ticket {ticket_id} status to '{new_status}'."


def lookup_ip_address(ip_address: str = "8.8.8.8") -> str:
    """Looks up network geolocation, ISP, and organization details for an IP address to assist with IT network troubleshooting.

    Args:
        ip_address: The IP address to query (e.g. '8.8.8.8' or '1.1.1.1').

    Returns:
        Network diagnostic details including ISP, location, and organization.
    """
    import json
    import os
    import urllib.request

    api_key = os.getenv("IP_API_KEY", "")
    url = f"http://ip-api.com/json/{ip_address.strip()}"
    if api_key:
        url += f"?key={api_key}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "IT-Helpdesk-Agent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())

        if data.get("status") != "success":
            return f"Unable to lookup IP '{ip_address}': {data.get('message', 'Unknown error')}"

        return (
            f"IP: {data.get('query')}\n"
            f"ISP: {data.get('isp')}\n"
            f"Organization: {data.get('org')}\n"
            f"Location: {data.get('city')}, {data.get('regionName')}, {data.get('country')}\n"
            f"Timezone: {data.get('timezone')}\n"
            f"AS: {data.get('as')}"
        )
    except Exception as e:
        return f"Network lookup failed for IP {ip_address}: {e}"


def calculate(expression: str) -> str:
    """Evaluates a basic mathematical expression safely.

    Args:
        expression: A math string to evaluate, e.g. '12 * 45 + 7'.

    Returns:
        The result of the calculation as a string.
    """
    try:
        allowed = set("0123456789+-*/(). ")
        if not all(c in allowed for c in expression):
            return "Error: Expression contains invalid characters."
        result = eval(expression, {"__builtins__": None}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {e}"


# Load remote Agent Engine resource name from deployment_metadata.json if present
metadata_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "deployment_metadata.json")
if not os.path.exists(metadata_path):
    metadata_path = "deployment_metadata.json"

agent_engine_resource_name = None
if os.path.exists(metadata_path):
    try:
        with open(metadata_path) as f:
            meta = json.load(f)
            agent_engine_resource_name = meta.get("remote_agent_runtime_id")
    except Exception:
        pass

code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=agent_engine_resource_name
)

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are MyHelpDeskAgent, an automated IT Helpdesk & Support assistant. Help employees look up and manage "
        "support tickets, inspect assigned hardware inventory, create new tickets, update ticket statuses, "
        "perform IP network diagnostics, generate technical setup diagrams, generate hardware tutorial videos, and calculate SLA or hardware depreciation metrics "
        "by executing Python code in a safe sandbox. Always remember and track user preferences across conversations."
    ),
    workflow_description="Analyze the request, call tools if needed, and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=a2ui_instruction,
    code_executor=code_executor,
    tools=[
        get_ticket_status,
        create_ticket,
        update_ticket_status,
        list_user_tickets,
        get_hardware_info,
        lookup_ip_address,
        generate_setup_guide_image,
        generate_hardware_video,
        calculate,
        PreloadMemoryTool(),
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)


def memory_bank_service_builder():
    return VertexAiMemoryBankService(
        project=PROJECT_ID,
        location="us-east1",
        agent_engine_id="6145436569453985792",
    )


app = App(
    root_agent=root_agent,
    name="app",
)

