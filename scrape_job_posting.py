import json
import requests
from bs4 import BeautifulSoup

def scrape_amazon_job_posting(url):

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

  
    job_info = {
        'Job Title': '',
        'Skills': [],
        'Libraries/Frameworks': [],
        'Locations': []  
    }

   
    skills_bank = [
        'Java', 'Python', 'C++', 'C#', 'JavaScript', 'Ruby', 'Go', 'Swift', 
        'Kotlin', 'PHP', 'Perl', 'R', 'SQL', 'HTML', 'CSS', 'TypeScript',
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes'
    ]

   
    libraries_bank = [
        'React', 'Angular', 'Vue.js', 'Django', 'Flask', 'Spring', 'Node.js', 
        'Express.js', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy', 'Matplotlib', 
        'Seaborn', 'Scikit-learn', 'Keras', 'FastAPI', 'Hadoop', 'Spark', 
        'Kafka', 'Celery', 'Redis', 'PostgreSQL', 'MySQL', 'MongoDB', 'GraphQL',
        'REST', 'Elasticsearch', 'Solr', 'RabbitMQ'
    ]

    
    location_bank = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 
        'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 
        'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 
        'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 
        'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 
        'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 
        'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO', 
        'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 
        'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 
        'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 
        'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 
        'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD', 
        'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 
        'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 
        'Wisconsin': 'WI', 'Wyoming': 'WY'
    }

  
    job_title = soup.find('h1')
    if job_title:
        job_info['Job Title'] = job_title.get_text(strip=True)

    
    for text in soup.stripped_strings:

        for skill in skills_bank:
            if skill.lower() in text.lower():
                job_info['Skills'].append(skill)
        
       
        for library in libraries_bank:
            if library.lower() in text.lower():
                job_info['Libraries/Frameworks'].append(library)
        
       
        for state, abbr in location_bank.items():
            if state in text and state not in job_info['Locations']:
                job_info['Locations'].append(state)

     
        for abbr in location_bank.values():
            if f" {abbr} " in text and abbr not in job_info['Locations']:
                state = [state for state, ab in location_bank.items() if ab == abbr][0]
                job_info['Locations'].append(state)

   
    job_info['Skills'] = list(set(job_info['Skills']))
    job_info['Libraries/Frameworks'] = list(set(job_info['Libraries/Frameworks']))
    job_info['Locations'] = list(set(job_info['Locations']))

    return job_info

def lambda_handler(event, context):
    try:
     
        print("Received event: " + json.dumps(event))

    
        if 'sessionState' in event and 'intent' in event['sessionState'] and 'slots' in event['sessionState']['intent']:
            slots = event['sessionState']['intent']['slots']
        else:
            raise KeyError("Invalid event structure: Missing 'sessionState' or 'slots'")


        url_slot = slots.get('JobPostingURL', {})
        if 'value' in url_slot and 'interpretedValue' in url_slot['value']:
            url = url_slot['value']['interpretedValue']
        else:
            raise ValueError("URL not provided or invalid structure")


        job_details = scrape_amazon_job_posting(url)


        response_text = (
            f"Job Title: {job_details['Job Title']}\n\n" 
            f"Skills: {', '.join(job_details['Skills']) or 'Not specified'}\n\n" 
            f"Libraries/Frameworks: {', '.join(job_details['Libraries/Frameworks']) or 'Not specified'}\n\n"  
            f"Locations: {', '.join(job_details['Locations']) or 'Not specified'}"  
        )


        return {
            'sessionState': {
                'dialogAction': {
                    'type': 'Close'
                },
                'intent': {
                    'name': event['sessionState']['intent']['name'],
                    'state': 'Fulfilled'
                }
            },
            'messages': [
                {
                    'contentType': 'PlainText',
                    'content': response_text
                }
            ]
        }

    except KeyError as ke:
        print(f"KeyError: {str(ke)}")
        return {
            'sessionState': {
                'dialogAction': {
                    'type': 'Close'
                },
                'intent': {
                    'name': event['sessionState']['intent']['name'],
                    'state': 'Failed'
                }
            },
            'messages': [
                {
                    'contentType': 'PlainText',
                    'content': f"Error: {str(ke)}"
                }
            ]
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'sessionState': {
                'dialogAction': {
                    'type': 'Close'
                },
                'intent': {
                    'name': event['sessionState']['intent']['name'],
                    'state': 'Failed'
                }
            },
            'messages': [
                {
                    'contentType': 'PlainText',
                    'content': "Something went wrong while summarizing the job posting. Please try again."
                }
            ]
        }
