import json
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

class CareerChatbot:
    def __init__(self):
        self.responses = {
            'greeting': [
                "Hello! I'm your career assistant. How can I help you today?",
                "Hi there! Ready to explore career options?",
                "Welcome! I'm here to help with your career questions."
            ],
            'career_advice': [
                "Based on your skills and education, I recommend focusing on roles that match your specialization.",
                "Consider roles that align with your degree and practical experience.",
                "Your profile suggests strong potential in technical roles. Have you considered upskilling in emerging technologies?"
            ],
            'skills_guidance': [
                "For your chosen career path, I recommend developing skills in modern frameworks and tools.",
                "Consider learning in-demand skills like cloud computing, AI/ML, or full-stack development.",
                "Technical skills combined with soft skills like communication will enhance your career prospects."
            ],
            'job_search': [
                "Start by updating your resume to highlight projects and relevant experience.",
                "Networking and online platforms like LinkedIn can help discover job opportunities.",
                "Consider internships or freelance projects to gain practical experience."
            ],
            'interview_tips': [
                "Prepare by researching the company and practicing common technical questions.",
                "Showcase your projects and be ready to explain your problem-solving approach.",
                "Focus on your strengths and how you can contribute to the organization."
            ],
            'fallback': [
                "I'm not sure I understand. Could you rephrase that?",
                "That's an interesting question! Could you provide more details?",
                "I specialize in career guidance. Feel free to ask about jobs, skills, or career paths."
            ]
        }

    def get_response(self, user_input):
        user_input = user_input.lower()
        
        # Keyword-based response matching
        if any(word in user_input for word in ['hello', 'hi', 'hey', 'greetings']):
            return random.choice(self.responses['greeting'])
        
        elif any(word in user_input for word in ['career', 'job', 'role', 'position']):
            return random.choice(self.responses['career_advice'])
        
        elif any(word in user_input for word in ['skill', 'learn', 'technology', 'programming']):
            return random.choice(self.responses['skills_guidance'])
        
        elif any(word in user_input for word in ['find job', 'search', 'apply', 'hiring']):
            return random.choice(self.responses['job_search'])
        
        elif any(word in user_input for word in ['interview', 'prepare', 'hiring process']):
            return random.choice(self.responses['interview_tips'])
        
        else:
            return random.choice(self.responses['fallback'])

# Global chatbot instance
chatbot = CareerChatbot()

@csrf_exempt
def chat_handler(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            if not user_message:
                return JsonResponse({'error': 'No message provided'}, status=400)
            
            bot_response = chatbot.get_response(user_message)
            
            return JsonResponse({
                'response': bot_response,
                'status': 'success'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)