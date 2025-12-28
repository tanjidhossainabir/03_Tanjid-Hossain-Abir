from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import RegistrationForm, EmployerProfileForm, JobSeekerProfileForm, JobForm, JobSearchForm
from .models import UserProfile, EmployerProfile, JobSeekerProfile, Job, JobApplication

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful!')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully.')
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('job_search')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'loginPage.html')


def home(request):
    """Simple home redirect: send authenticated users to their main page, else to login."""
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.user_type == 'job_seeker':
                return redirect('job_search')
            else:
                return redirect('skill_matching_dashboard')
        except UserProfile.DoesNotExist:
            return redirect('login')
    return redirect('login')

@login_required
def create_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.user_type == 'employer':
        if request.method == 'POST':
            form = EmployerProfileForm(request.POST)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user_profile = user_profile
                profile.save()
                messages.success(request, 'Employer profile created successfully!')
                return redirect('home')
        else:
            form = EmployerProfileForm()
        return render(request, 'employer_profile.html', {'form': form})
    elif user_profile.user_type == 'job_seeker':
        if request.method == 'POST':
            form = JobSeekerProfileForm(request.POST, request.FILES)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user_profile = user_profile
                profile.save()
                messages.success(request, 'Job Seeker profile created successfully!')
                return redirect('home')
        else:
            form = JobSeekerProfileForm()
        return render(request, 'jobseeker_profile.html', {'form': form})
    else:
        messages.error(request, 'Invalid user type.')
        return redirect('home')


@login_required
def post_job(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.user_type != 'employer':
        messages.error(request, 'Only employers can post jobs.')
        return redirect('home')

    employer_profile = get_object_or_404(EmployerProfile, user_profile=user_profile)

    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = employer_profile
            job.save()
            messages.success(request, 'Job posted successfully.')
            return redirect('skill_matching_dashboard')
    else:
        form = JobForm()

    return render(request, 'post_job.html', {'form': form})


@login_required
def edit_profile(request):
    """Allow employers and job seekers to edit their profile information."""
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if user_profile.user_type == 'employer':
        try:
            profile = EmployerProfile.objects.get(user_profile=user_profile)
        except EmployerProfile.DoesNotExist:
            profile = None

        if request.method == 'POST':
            form = EmployerProfileForm(request.POST, instance=profile)
            if form.is_valid():
                prof = form.save(commit=False)
                prof.user_profile = user_profile
                prof.save()
                messages.success(request, 'Employer profile updated.')
                return redirect('skill_matching_dashboard')
        else:
            form = EmployerProfileForm(instance=profile)

        return render(request, 'edit_profile.html', {'form': form, 'user_type': 'employer'})

    elif user_profile.user_type == 'job_seeker':
        try:
            profile = JobSeekerProfile.objects.get(user_profile=user_profile)
        except JobSeekerProfile.DoesNotExist:
            profile = None

        if request.method == 'POST':
            form = JobSeekerProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                prof = form.save(commit=False)
                prof.user_profile = user_profile
                prof.save()
                messages.success(request, 'Job seeker profile updated.')
                return redirect('job_search')
        else:
            form = JobSeekerProfileForm(instance=profile)

        return render(request, 'edit_profile.html', {'form': form, 'user_type': 'job_seeker'})

    else:
        messages.error(request, 'Invalid user type.')
        return redirect('home')

@login_required
def job_search(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.user_type != 'job_seeker':
        messages.error(request, 'Only job seekers can access this page.')
        return redirect('home')

    try:
        job_seeker_profile = JobSeekerProfile.objects.get(user_profile=user_profile)
    except JobSeekerProfile.DoesNotExist:
        messages.info(request, 'Please create your Job Seeker profile first.')
        return redirect('create_profile')

    if request.method == 'POST':
        job_id = request.POST.get('job_id')
        if job_id:
            job = get_object_or_404(Job, id=job_id)
            if not JobApplication.objects.filter(job=job, applicant=job_seeker_profile).exists():
                JobApplication.objects.create(job=job, applicant=job_seeker_profile)
                messages.success(request, f'You have applied for {job.title}.')
            else:
                messages.info(request, 'You have already applied for this job.')
        return redirect('job_search')

    form = JobSearchForm(request.GET)
    jobs = Job.objects.all()

    if form.is_valid():
        keyword = form.cleaned_data.get('keyword')
        category = form.cleaned_data.get('category')
        if keyword:
            jobs = jobs.filter(Q(title__icontains=keyword) | Q(skills_required__icontains=keyword))
        if category:
            jobs = jobs.filter(category__icontains=category)

    applied_jobs = JobApplication.objects.filter(applicant=job_seeker_profile).values_list('job_id', flat=True)

    context = {
        'form': form,
        'jobs': jobs,
        'applied_jobs': applied_jobs,
    }
    return render(request, 'job_search.html', context)

@login_required
def skill_matching_dashboard(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    context = {'user_type': user_profile.user_type}

    if user_profile.user_type == 'job_seeker':
        job_seeker_profile = get_object_or_404(JobSeekerProfile, user_profile=user_profile)
        seeker_skills = set(skill.strip().lower() for skill in job_seeker_profile.skills.split(',') if skill.strip())

        matched_jobs = []
        jobs = Job.objects.all()
        for job in jobs:
            job_skills = set(skill.strip().lower() for skill in job.skills_required.split(',') if skill.strip())
            matched_skills = seeker_skills.intersection(job_skills)
            if matched_skills:
                match_percentage = int((len(matched_skills) / len(job_skills)) * 100) if job_skills else 0
                matched_jobs.append({
                    'job': job,
                    'matched_skills': list(matched_skills),
                    'match_percentage': match_percentage
                })

        matched_jobs.sort(key=lambda x: x['match_percentage'], reverse=True)
        context['matched_jobs'] = matched_jobs

    elif user_profile.user_type == 'employer':
        employer_profile = get_object_or_404(EmployerProfile, user_profile=user_profile)
        jobs = Job.objects.filter(employer=employer_profile)

        matched_candidates = []
        for job in jobs:
            job_skills = set(skill.strip().lower() for skill in job.skills_required.split(',') if skill.strip())
            candidates = JobSeekerProfile.objects.all()
            for candidate in candidates:
                candidate_skills = set(skill.strip().lower() for skill in candidate.skills.split(',') if skill.strip())
                matched_skills = candidate_skills.intersection(job_skills)
                if matched_skills:
                    match_percentage = int((len(matched_skills) / len(job_skills)) * 100) if job_skills else 0
                    matched_candidates.append({
                        'job': job,
                        'candidate': candidate,
                        'matched_skills': list(matched_skills),
                        'match_percentage': match_percentage
                    })

        matched_candidates.sort(key=lambda x: x['match_percentage'], reverse=True)
        context['matched_candidates'] = matched_candidates

    else:
        messages.error(request, 'Invalid user type.')
        return redirect('home')

    return render(request, 'skill_matching_dashboard.html', context)
