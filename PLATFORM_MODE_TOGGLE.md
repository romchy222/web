# Platform Mode Toggle Feature

## Overview

The platform now supports two operational modes that can be toggled from the Django admin panel:

### 1. LMS Mode (Default)
Full learning management system with all features:
- Course catalog
- Enrollment system
- Progress tracking
- Certificates
- Instructor dashboard
- Student profiles

### 2. Applications Mode
Pre-registration landing page for collecting course applications before launch:
- Simple landing page with application form
- Collects applicant information
- Admin panel for managing applications
- Automatic redirect from all pages to landing page

## How to Use

### Switching Modes

1. Log in to Django Admin Panel: `http://your-domain/admin/`
2. Navigate to **Platform Settings** (⚙️ Platform Mode Settings)
3. Click on the settings entry
4. Change the **Platform Mode** dropdown:
   - Select **LMS Mode** for full platform
   - Select **Applications Mode** for landing page
5. Click **Save**

The change takes effect immediately - no server restart required.

### Managing Applications (Application Mode)

When in Application Mode, users can submit pre-registration forms. Administrators can manage these applications:

1. Go to Django Admin Panel
2. Navigate to **Course Applications**
3. View all submitted applications with:
   - Applicant name and contact info
   - Course interest
   - Submission date
   - Processing status

4. Use bulk actions to:
   - Mark applications as processed
   - Export data
   - Add admin notes

### Customizing Landing Page

In the Platform Settings, you can customize:

- **Landing Page Title**: Main headline (default: "Скоро открытие!")
- **Landing Page Description**: Subtext below title
- **Enable Application Form**: Toggle to show/hide the form

## Technical Details

### Models

**PlatformSettings** (Singleton)
- `mode`: Choice field (lms/applications)
- `landing_page_title`: Customizable title
- `landing_page_description`: Customizable description
- `application_form_enabled`: Boolean to toggle form

**CourseApplication**
- `first_name`, `last_name`: Applicant name
- `email`, `phone`: Contact information
- `course_interest`: Interested course
- `message`: Additional information
- `submitted_at`: Timestamp
- `processed`: Admin processing status
- `notes`: Admin notes

### Middleware/Decorator

The `@check_platform_mode` decorator:
- Checks current platform mode before rendering views
- Redirects to landing page if in application mode
- Excludes admin panel from redirection

### URLs

- `/landing/` - Landing page (accessible in both modes)
- `/submit-application/` - Form submission endpoint
- All other URLs redirect to `/landing/` when in application mode

## Use Cases

### Pre-Launch Phase
1. Set mode to **Applications**
2. Customize landing page text
3. Share landing page URL with potential students
4. Collect pre-registrations
5. Review applications in admin panel

### Launch Phase
1. Review and process all applications
2. Set mode to **LMS**
3. Contact applicants about platform launch
4. Platform immediately available with full features

### Maintenance/Updates
Switch to Applications mode during major updates to show "coming soon" page while maintaining the system.

## Screenshots

### Landing Page (Application Mode)
![Landing Page](https://github.com/user-attachments/assets/b365c1e8-826f-40de-851e-846c0a7c5a0f)

### Admin Panel - Platform Settings
The settings appear at the top of the admin panel with a clear mode indicator:
- 🎓 Green for LMS Mode
- 📝 Yellow for Applications Mode

### Admin Panel - Course Applications
View and manage all pre-registration applications with filtering and bulk actions.

## Benefits

1. **No Code Changes**: Switch modes via admin panel
2. **Data Retention**: All LMS data remains intact in application mode
3. **Professional**: Clean landing page for pre-launch marketing
4. **Lead Generation**: Collect interested students before launch
5. **Flexible**: Easy to toggle based on needs
6. **Safe**: Admin panel always accessible regardless of mode

## Migration

The feature adds two new database tables:
- `courses_platformsettings`
- `courses_courseapplication`

Run migrations to enable:
```bash
python manage.py migrate
```

## API Behavior

In Application Mode:
- Web interface redirects to landing page
- API endpoints remain accessible (for mobile apps, integrations)
- Admin panel remains fully functional

This allows maintaining API services while showing a "coming soon" page to web visitors.
