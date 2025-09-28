from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils.text import slugify
import requests
from urllib.parse import urlparse


@login_required
@require_http_methods(["GET"])
def download_attachment(request, model_name, pk):
    """
    Server-side download view that works better with Safari.
    Downloads files from Cloudinary and serves them with proper headers.
    """
    # Import models dynamically to avoid circular imports
    if model_name == "expense":
        from expenses.models import Expense

        model = Expense
    elif model_name == "income":
        from income.models import Income

        model = Income
    elif model_name == "subscription":
        from subscriptions.models import Subscription

        model = Subscription
    else:
        raise Http404("Invalid model type")

    # Get the object and ensure user owns it
    obj = get_object_or_404(model, pk=pk, user=request.user)

    if not obj.attachment:
        raise Http404("No attachment found")

    try:
        # Get the Cloudinary URL
        cloudinary_url = obj.attachment.url

        # Fetch the file from Cloudinary
        response = requests.get(cloudinary_url, stream=True)
        response.raise_for_status()

        # Extract filename from URL
        parsed_url = urlparse(cloudinary_url)
        filename = parsed_url.path.split("/")[-1]

        # Create a better filename using the object's name/description
        if model_name == "expense":
            base_name = slugify(obj.description)
        elif model_name == "income":
            base_name = slugify(obj.description)
        elif model_name == "subscription":
            base_name = slugify(obj.name)
        else:
            base_name = "attachment"

        # Get file extension
        file_extension = filename.split(".")[-1] if "." in filename else "file"
        download_filename = f"{base_name}.{file_extension}"

        # Create Django response with proper headers
        django_response = HttpResponse(
            response.content,
            content_type=response.headers.get(
                "content-type", "application/octet-stream"
            ),
        )

        # Set headers to force download in Safari
        django_response["Content-Disposition"] = (
            f'attachment; filename="{download_filename}"'
        )
        django_response["Content-Length"] = str(len(response.content))
        django_response["Cache-Control"] = "no-cache, no-store, must-revalidate"
        django_response["Pragma"] = "no-cache"
        django_response["Expires"] = "0"

        return django_response

    except requests.RequestException as e:
        raise Http404(f"Error downloading file: {e}")
    except Exception as e:
        raise Http404(f"Unexpected error: {e}")
