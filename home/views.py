from django.shortcuts import render, redirect
from admin_datta.forms import RegistrationForm, LoginForm, UserPasswordChangeForm, UserPasswordResetForm, UserSetPasswordForm
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetConfirmView, PasswordResetView
from django.views.generic import CreateView
from django.contrib.auth import logout

from .models import *

def index(request):

  context = {
    'segment'  : 'index',
    #'products' : Product.objects.all()
  }
  return render(request, "pages/index.html", context)



from django.shortcuts import render, redirect
from .forms import WeekEntryForm
from django.http import HttpResponse
from .models import WeekEntry
from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import render
from .models import Bay, Bed, Variety


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# def user_login(request):
#     if request.method == "POST":
#         username = request.POST.get('username', '')  
#         password = request.POST.get('password', '')  
#         user = authenticate(request, username=username, password=password)

#         if user is not None:
#             login(request, user)
#             print("User authenticated successfully!")  # Debugging
#             return redirect('week_form')
#         else:
#             messages.error(request, "Invalid username or password.")
#             print("Authentication failed.")  # Debugging

#     return render(request, 'accounts/signin.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def week_form(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'forms/week_form.html', {'user': request.user})
@login_required
def form_view(request):
    bays = Bay.objects.all()
    return render(request, 'forms/form.html', {'bays': bays})
@login_required
def get_beds(request):
    bay_id = request.GET.get('bay_id')
    beds = Bed.objects.filter(bay_id=bay_id).values('id', 'code')
    return JsonResponse({'beds': list(beds)})
@login_required
def get_varieties(request):
    bed_id = request.GET.get('bed_id')
    varieties = Variety.objects.filter(bed_id=bed_id).values('id', 'name')
    return JsonResponse({'varieties': list(varieties)})
@login_required
def week_entry_form(request):
    bays = Bay.objects.all()
    return render(request, 'week_entry_form.html', {'bays': bays})
@login_required
def fetch_beds(request):
    bay_id = request.GET.get('bay_id')
    beds = Bed.objects.filter(bay_id=bay_id).values('id', 'code')   
    return JsonResponse({'beds': list(beds)})
@login_required
def fetch_varieties(request):
    bed_id = request.GET.get('bed_id')
    varieties = Variety.objects.filter(bed_id=bed_id).values('id', 'name')   
    return JsonResponse({'varieties': list(varieties)})

@login_required
def submit_week_entry(request):
    if request.method == 'POST':
        week = request.POST.get('week')
        bed_no = request.POST.get('bed_no')
        variety = request.POST.get('variety')
        amounts = request.POST.get('amounts')

        if not all([week, bed_no, variety, amounts]):
            messages.error(request, "❌ Missing form data!")
            return redirect('week_entry_form')

        try:
            WeekEntry.objects.create(week=week, bed_no_id=bed_no, variety_id=variety, amounts=amounts)
            messages.success(request, "✅ Form submitted successfully!")
        except Exception as e:
            messages.error(request, f"❌ Error saving data: {e}")

        return redirect('forms/week_entry_form')

@login_required
def week_form(request):
    bays = Bay.objects.all()
    beds = Bed.objects.all()
    varieties = Variety.objects.all()

    context = {
        'bays': bays,
        'beds': beds,
        'varieties': varieties,
    }
    
    return render(request, 'forms/week_form.html', context)


# --------------------------------------------------------------------

from django.shortcuts import render
from .models import DataEntry

@login_required
def data_table(request):
    entries = DataEntry.objects.all()  # Fetch stored data
    print(entries)  # Debugging: Check if data is retrieved
    return render(request, 'data_table.html', {'entries': entries})
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .models import WeekEntry, Bay, Bed, Variety

def submit_week_entry(request):
    if request.method == 'POST':
        week = request.POST.get('date')  # Capturing week from form
        bay_id = request.POST.get('bay')
        bed_id = request.POST.get('bed_no')
        variety_id = request.POST.get('variety')
        amounts = request.POST.get('amounts')

        if not all([week, bay_id, bed_id, variety_id, amounts]):
            return HttpResponse("Missing form data", status=400)

        try:
            bay = Bay.objects.get(id=bay_id)
            bed = Bed.objects.get(id=bed_id)
            variety = Variety.objects.get(id=variety_id)

            WeekEntry.objects.create(
                week=week,
                bay=bay,
                bed=bed,
                variety=variety,
                amounts=amounts,
                submitted_by=request.user
            )

            return JsonResponse({"message": "Entry added successfully!"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)

def week_entries(request):
    entries = WeekEntry.objects.all().order_by('-week')  # Latest first
    return render(request, "forms/week_entries.html", {"entries": entries})

from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now
from datetime import timedelta
from .models import WeekEntry

def user_entries_list(request):
    """
    Display only the current user's submissions.
    Allow editing for 12 hours after submission.
    """
    user = request.user
    twelve_hours_ago = now() - timedelta(hours=12)

    # Get the user's own entries
    entries = WeekEntry.objects.filter(submitted_by=user)

    # Add a flag to check if the entry is still editable
    for entry in entries:
        entry.is_editable = entry.created_at >= twelve_hours_ago

    return render(request, "forms/user_entries.html", {"entries": entries})

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .forms import WeekEntryForm

@login_required
def edit_entry(request, entry_id):
    """
    Allow the user to edit their submission within 12 hours.
    """
    entry = get_object_or_404(WeekEntry, id=entry_id, submitted_by=request.user)
    twelve_hours_ago = now() - timedelta(hours=12)

    if entry.created_at < twelve_hours_ago:
        return HttpResponseForbidden("Editing time expired.")

    if request.method == "POST":
        form = WeekEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect("user_entries_list")
    else:
        form = WeekEntryForm(instance=entry)

    return render(request, "forms/edit_entry.html", {"form": form})

from django.http import JsonResponse
from .models import WeekEntry

def get_entry_data(request, entry_id):
    """
    Fetch entry data for editing via AJAX.
    """
    try:
        # Retrieve the entry
        entry = WeekEntry.objects.get(id=entry_id, submitted_by=request.user)

        # Return the data as JSON
        data = {
            'bay': entry.bay.name,  # Assuming there's a related model for Bay
            'bed_no': entry.bed_no.code,  # Assuming there's a related model for Bed
            'variety': entry.variety.name,  # Assuming there's a related model for Variety
            'amounts': entry.amounts,
            'date': entry.date.strftime('%Y-%m-%d'),  # Format date as needed
        }
        return JsonResponse(data)
    except WeekEntry.DoesNotExist:
        return JsonResponse({'error': 'Entry not found or not authorized to view this entry.'}, status=404)

