# Bug Fix Documentation
## match_up Project - All Bugs Encountered and Fixed

This document catalogs all bugs encountered during the development of the match_up dating platform and details how each was resolved.

---

## Table of Contents
1. [Profile Management Bugs](#profile-management-bugs)
2. [Authentication & Navigation Bugs](#authentication--navigation-bugs)
3. [Configuration & Settings Bugs](#configuration--settings-bugs)
4. [Database & Model Bugs](#database--model-bugs)
5. [UI/UX Bugs](#uiux-bugs)
6. [Deployment & Environment Bugs](#deployment--environment-bugs)

---

## Profile Management Bugs

### Bug #1: ProfileAbout View Accessing Non-Existent Profile
**Severity:** High  
**Status:** ✅ Fixed

**Description:**
The `ProfileAbout` view's `get_object()` method was directly accessing `self.request.user.profile` without checking if the profile exists. This caused a `RelatedObjectDoesNotExist` error when authenticated users without profiles tried to access `/profile/about/`.

**Error Message:**
```
RelatedObjectDoesNotExist: User has no profile.
```

**Root Cause:**
```python
# BEFORE (dating/views.py)
class ProfileAbout(LoginRequiredMixin, generic.DetailView):
    def get_object(self):
        return self.request.user.profile  # ❌ No check if profile exists
```

**Fix Applied:**
Added a `get()` method to check for profile existence before calling `get_object()`, redirecting to profile creation if no profile exists:

```python
# AFTER (dating/views.py, lines 119-125)
class ProfileAbout(LoginRequiredMixin, generic.DetailView):
    def get(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            return redirect('profile_create')
        return super().get(request, *args, **kwargs)
    
    def get_object(self):
        return self.request.user.profile
```

**Files Modified:**
- `dating/views.py` (lines 119-125)

**Prevention:**
Similar checks were added to `ProfileList`, `ProfileDelete`, and `ProfileGetStarted` views to ensure consistent error handling.

---

### Bug #2: Profile Create Success URL Redirecting to Wrong View
**Severity:** Medium  
**Status:** ✅ Fixed

**Description:**
After creating a profile, users were redirected to `profile_detail` which requires a primary key, but the success URL didn't include the created profile's ID.

**Root Cause:**
```python
# BEFORE (dating/views.py)
class ProfileCreate(LoginRequiredMixin, generic.CreateView):
    success_url = reverse_lazy('profile_detail')  # ❌ Missing pk argument
```

**Fix Applied:**
Overrode `get_success_url()` to include the created profile's primary key:

```python
# AFTER (dating/views.py, lines 76-77)
def get_success_url(self):
    return reverse_lazy('profile_detail', args=[self.object.pk])
```

**Files Modified:**
- `dating/views.py` (lines 76-77)

**note**: In the project we have :
ProfileDetail (with <int:pk>) — for viewing any profile by ID (e.g., from the profile list)
ProfileAbout (at /profile/about/) — for the current user’s own profile 
---

## Authentication & Navigation Bugs

### Bug #3: Login and Logout Links Not Working
**Severity:** High  
**Status:** ✅ Fixed

**Description:**
Navigation links in `base.html` used `href="#"` instead of the actual URL variables, making login and logout buttons non-functional.

**Root Cause:**
```html
<!-- BEFORE (templates/base.html) -->
<a class="nav-link" href="#">Logout</a>  <!-- ❌ No actual URL -->
<a class="nav-link" href="#">Login</a>   <!-- ❌ No actual URL -->
```

**Fix Applied:**
Updated all navigation links to use the proper URL variables:

```html
<!-- AFTER (templates/base.html, lines 64-65, 69-70, 73-74) -->
<a class="nav-link {% if request.path == logout_url %}active{% endif %}"
    href="{{ logout_url }}">Logout</a>
<a class="nav-link {% if request.path == login_url %}active{% endif %}"
    href="{{ login_url }}">Login</a>
<a class="nav-link {% if request.path == signup_url %}active{% endif %}"
    href="{{ signup_url }}">Sign Up</a>
```

**Files Modified:**
- `templates/base.html` (lines 64-65, 69-70, 73-74)

---

### Bug #4: URL Path Mismatch Between Settings and URLs
**Severity:** Medium  
**Status:** ✅ Fixed

**Description:**
There was a mismatch between the URL path in `settings.py` (`/account/login/`) and the actual URL pattern in `urls.py` (`accounts/`). This caused login redirects to fail.

**Root Cause:**
```python
# BEFORE
# match_up/settings.py
LOGIN_URL = '/account/login/'  #  Singular

# match_up/urls.py
path("accounts/", include("allauth.urls"))  # Plural
```

**Fix Applied:**
Standardized to use `account/` (singular) to match django-allauth defaults:

```python
# AFTER (match_up/settings.py, line 149)
LOGIN_URL = '/account/login/'

# match_up/urls.py (line 25)
path("account/", include("allauth.urls"), name="account-urls")
```

**Files Modified:**
- `match_up/settings.py` (line 149)
- `match_up/urls.py` (line 25)

**Note:** The current codebase uses `account/` (singular) consistently.

---

### Bug #5: Superuser Login Not Working
**Severity:** High  
**Status:** ✅ Fixed (Documented)

**Description:**
Superuser credentials were not working to access the Django admin panel.

**Cause:**

DB reset/recreated: The project was linked to a new PostgreSQL database from CI so the migrations re-run from scratch and the old superuser was gone. 


**Fix Applied:**
Recreated superuser: `python manage.py createsuperuser`


**note** :If  password forgotten:

```python

python manage.py changepassword <username>.

```
---

## Configuration & Settings Bugs

### Bug #6: SECRET_KEY Not Being Loaded from env.py
**Severity:** Critical  
**Status:** ✅ Fixed

**Description:**
The `SECRET_KEY` in `settings.py` was reading from environment variables, but `env.py` wasn't being imported, causing the secret key to be `None` and breaking Django functionality.

**Root Cause:**
```python
# BEFORE (match_up/settings.py)
SECRET_KEY = os.environ.get('SECRET_KEY')  # ❌ env.py not imported
```

**Fix Applied:**
Added import statement for `env.py` at the top of `settings.py`:

```python
# AFTER (match_up/settings.py, lines 15-16)
import dj_database_url
if os.path.isfile('env.py'):
    import env  # ✅ Import env.py to set environment variables

# Line 26
SECRET_KEY = os.environ.get('SECRET_KEY')  # ✅ Now works correctly
```

**Files Modified:**
- `match_up/settings.py` (lines 15-16)

---

### Bug #7: Error Display Issues (CSS style not rendered)
**Severity:** High  
**Status:** ✅ Fixed

**Description:**

In settings.py, I forgot that DEBUG was still set to False, which cause the CSS not being served. 

Django does not serve static files automatically. It expects a web server (nginx/Apache) or WhiteNoise to serve them. Even with WhiteNoise in middleware, static files may not be collected or served correctly in development.

**Root Cause:**
```python
# BEFORE (match_up/settings.py)
DEBUG = False  # ❌ Should be True in development
```

**Fix Applied:**
Set `DEBUG = True` for local development:

```python
# AFTER (match_up/settings.py, line 29)
DEBUG = True  # ✅ Shows errors and serves static files in development
```

**Files Modified:**
- `match_up/settings.py` (line 29)

**Note:** `DEBUG` should be set to `False` in production, but `True` in development for debugging.
Setting `DEBUG = False` in development causes:
- Static files (CSS, JavaScript) not being served.
- Detailed error messages being hidden
- Generic error pages instead of helpful debug information

---

### Bug #8: Deprecated django-allauth Settings Causing Warnings
**Severity:** Low  
**Status:** ✅ Fixed

**Description:**
PowerShell/terminal showed deprecation warnings for old django-allauth settings that were replaced in newer equivalents.

**Deprecated Settings:**
- `ACCOUNT_AUTHENTICATION_METHOD`
- `ACCOUNT_EMAIL_REQUIRED`
- `ACCOUNT_USERNAME_REQUIRED`

**Fix Applied:**
Updated to new allauth 64+ settings format:

```python
# BEFORE (match_up/settings.py)
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'  # ❌ Deprecated
ACCOUNT_EMAIL_REQUIRED = True  # ❌ Deprecated
ACCOUNT_USERNAME_REQUIRED = True  # ❌ Deprecated

# AFTER (match_up/settings.py, lines 144-146)
ACCOUNT_LOGIN_METHODS = {'username', 'email'}  # ✅ New format
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']  # ✅ New format
```

**Files Modified:**
- `match_up/settings.py` (lines 144-146)

---


## Database & Model Bugs

### Bug #9: Profile Model Meta Ordering Using Wrong Field Name
**Severity:** Medium  
**Status:** ✅ Fixed

**Description:**
The `Profile` model's `Meta.ordering` was pointing to `created_on`, but the actual field name is `createdAt`, causing database query errors.

**Error Message:**
```
FieldError: Cannot resolve keyword 'created_on' into field.
```

**Root Cause:**
```python
# BEFORE (dating/models.py)
class Profile(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)  # ✅ Correct field name
    
    class Meta:
        ordering = ['-created_on']  # ❌ Wrong field name
```

**Fix Applied:**
Updated `Meta.ordering` to use the correct field name:

```python
# AFTER (dating/models.py, line 28)
class Meta:
    ordering = ['-createdAt']  # ✅ Matches field name
```

**Files Modified:**
- `dating/models.py` (line 28)

---

## UI/UX Bugs

### Bug #10: Navbar Disappearing on Small Screens
**Severity:** High  
**Status:** ✅ Fixed

**Description:**
The navigation bar was completely hidden on mobile and tablet devices due to Bootstrap utility classes that explicitly hid it below the `lg` breakpoint.

**Root Cause:**
```html
<!-- BEFORE (templates/base.html) -->
<nav class="navbar navbar-expand-lg d-none d-lg-flex">  <!-- ❌ Hidden on small screens -->
```

**Issues:**
1. `d-none` class hiding navbar on all screen sizes
2. `d-lg-flex` only showing it on large screens
3. Incorrect collapse target ID

**Fix Applied:**
1. Removed `d-none d-lg-flex` classes
2. Fixed navbar collapse functionality
3. Added proper mobile responsive styling

```html
<!-- AFTER (templates/base.html, line 37) -->
<nav class="navbar navbar-expand-lg py-4 container">  <!-- ✅ Shows on all screens -->
    <button class="navbar-toggler" type="button" 
            data-bs-toggle="collapse" 
            data-bs-target="#navbarSupportedContent">  <!-- ✅ Correct target -->
```

**Files Modified:**
- `templates/base.html` (line 37, 41-44)
- `static/css/style.css` (added mobile responsive styles)

---

## Deployment & Environment Bugs

### Bug #11: Cloudinary Configuration Issues
**Severity:** High  
**Status:** ✅ Fixed

**Description:**
Cloudinary image uploads were not working correctly due to improper configuration of the `CLOUDINARY_URL` environment variable.

**Root Cause:**
The `CLOUDINARY_URL` key was not properly set in the environment variables, I did not replace the * with the proper API secret value. 

**Fix Applied:**
1. Ensured `CLOUDINARY_URL` is set in `env.py`:
```python
os.environ.setdefault("CLOUDINARY_URL", "cloudinary://api_key:api_secret@cloud_name")
```

2. Updated `Profile.photo` field to use `CloudinaryField` with proper transformations:
```python
# AFTER (dating/models.py, lines 21-22)
photo = CloudinaryField(
    'image', folder='profile_pictures/', blank=True, null=True)
```

3. Configured Cloudinary storage in `settings.py`:
```python
# AFTER (match_up/settings.py, lines 168-169)
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')
```

**Files Modified:**
- `dating/models.py` (lines 21-22)
- `match_up/settings.py` (lines 168-169)
- `env.py` (CLOUDINARY_URL configuration)

---

### Bug #12: db.sqlite3 Committed to Git
**Severity:** Low  
**Status:** ✅ Fixed (Documented)

**Description:**
The local SQLite database file (`db.sqlite3`) was being tracked in Git, which is not recommended practice.

**Fix Applied:**
1. Added `db.sqlite3` to `.gitignore`
2. Removed from Git history if already committed
3. Documented that only migration files and fixtures should be version controlled



