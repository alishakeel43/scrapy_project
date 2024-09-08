from django.http import JsonResponse
from django.shortcuts import render , redirect
from .forms import ScrapyForm
from .services import ScrapingService,SpiderFileService
from .models import Record, WebsiteXPath
from django.db import IntegrityError, transaction
from django.contrib import messages

def scrape_view(request):
    if request.method == 'GET':
        request.session.pop('form_data', None)
        request.session.pop('scraped_records', None)
        form = ScrapyForm()

    
    return render(request, 'spidersweb/scrape_form.html', {'form': form})


def scrapy_submit(request):
    if request.method == 'POST':
        form_data = request.session.get('form_data')
        scraped_records = request.session.get('scraped_records')

        if form_data and scraped_records:

            # Store records in the database
            if store_records_in_db(request):

                #  with create spider file 
                # file_created = generate_spider_file(request)
                
                # messages.success(request, f'Form submitted and data stored successfully! And Spider File is {"" if file_created else "not"} created')
                
                 #  without creation of spider file 
                messages.success(request, f'Form submitted and data stored successfully!')
            else:
                messages.error(request, 'Failed to store data in the database.')
        else:
            messages.error(request, 'Unable to store records in the database.')
            
    return redirect('scrape_view')  # Replace with the name of your URL pattern or a URL

def store_records_in_db(request):
    form_data = request.session.get('form_data')
    scraped_records = request.session.get('scraped_records')

    if form_data and scraped_records:
        filtered_scraped_records = {k: v for k, v in scraped_records.items() if v}

        try:
            with transaction.atomic():

                record = Record.objects.filter(city=form_data['city'], state_id=form_data['state_id']).first()

                if record:
                    # Check if the website has changed
                    if form_data['website'] != record.website:
                        # Update the website if it has changed
                        record.website = form_data['website']
                    
                    # Update other fields
                    for field, value in filtered_scraped_records.items():
                        # Check if the field exists in the model and if the value is not None
                        if hasattr(record, field) and value is not None:
                            setattr(record, field, value)
                    
                    # Save the updated record
                    record.save()

                filtered_form_data = {k: v for k, v in form_data.items() if v and k not in ['city', 'state_id', 'website']}

                WebsiteXPath.objects.update_or_create(
                    city=form_data['city'],
                    state_id=form_data['state_id'],
                    website=form_data['website'],
                    defaults=filtered_form_data
                )

                return True

        except IntegrityError as e:
            print(f"IntegrityError: {e}")
            return False

    return False

def view_records(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = ScrapyForm(request.POST)
        if form.is_valid():
            data = {
                'city': form.cleaned_data['city'],
                'state_id': form.cleaned_data['state_id'],
                'website': form.cleaned_data['website'],
                'municipality_main_tel_xpath': form.cleaned_data['municipality_main_tel_xpath'],
                'building_department_main_email_xpath': form.cleaned_data['building_department_main_email_xpath'],
                'building_department_main_phone_xpath': form.cleaned_data['building_department_main_phone_xpath'],
                'chief_building_official_name_xpath': form.cleaned_data['chief_building_official_name_xpath'],
            }
            
            xpaths = [
                {"building_department_main_phone": form.cleaned_data['building_department_main_phone_xpath']},
                {"building_department_main_email": form.cleaned_data['building_department_main_email_xpath']},
                {"municipality_main_tel": form.cleaned_data['municipality_main_tel_xpath']},
                {"chief_building_official_name": form.cleaned_data['chief_building_official_name_xpath']}
            ]

            service = ScrapingService(
                city=form.cleaned_data['city'],
                state_id=form.cleaned_data['state_id'],
                website=form.cleaned_data['website'],
                xpaths=xpaths
            )


            records = service.getData()

            if all(value is None or value == "" for value in records.values()):
                return JsonResponse({
                    'message': 'No valid data was extracted. Please try again with the correct XPaths.'
                }, status=200)

            request.session['form_data'] = data
            request.session['scraped_records'] = records

            result = {
                'message': f"Processed data for {form.cleaned_data['city']}, {form.cleaned_data['state_id']}",
                'records': records
            }
            return JsonResponse(result)
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    else:
        form = ScrapyForm()
        return render(request, 'spidersweb/scrape_form.html', {'form': form})

def check_website(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = ScrapyForm(request.POST)
        if form.is_valid():
            website = form.cleaned_data['website']
            city = form.cleaned_data['city']
            state_id = form.cleaned_data['state_id']
            
            record = Record.objects.filter(city=city, state_id=state_id).first()
            if record and record.website != website:
                old_website = record.website
                return JsonResponse(
                    {
                        'needs_update': True,
                        'old_website_url': old_website,
                        'new_website_url': website
                    }
                    )
            else:
                return JsonResponse({'needs_update': False})
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

def check_website_url(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form_data = request.POST
        city = form_data.get('city')
        state_id = form_data.get('state_id')
        new_website_url = form_data.get('website')
        
        record = Record.objects.filter(city=city, state_id=state_id).first()
        
        if record:
            old_website_url = record.website
            if old_website_url != new_website_url:
                return JsonResponse({
                    'website_diff': True,
                    'old_website_url': old_website_url,
                    'new_website_url': new_website_url
                })
        
        return JsonResponse({'website_diff': False})



def generate_spider_file(request):

    form_data = request.session.get('form_data')

    if form_data:
        city = form_data['city'] 
        state_id = form_data['state_id']
        website_url = form_data['website']
        xpaths = {
            'building_department_main_phone': form_data['building_department_main_phone_xpath'],
            'building_department_main_email': form_data['building_department_main_email_xpath'],
            'municipality_main_tel': form_data['municipality_main_tel_xpath'],
            'chief_building_official_name': form_data['chief_building_official_name_xpath'],
        }

        # Initialize the service
        spider_service = SpiderFileService(city=city, state_id=state_id, website_url=website_url, xpaths=xpaths)

        # Create or update the spider
        spider_service.create_or_update_spider()

        return True

    return False