from django.core.exceptions import ValidationError

class ContainsLetterValidator:
    def validate(self , password , user = None):
        if not any(char.isalpha() for char in password):
            raise ValidationError('le mot de passe doit contenir une lettre' , code= 'password no letters')
        


    def get_help_text(self):
        return 'Le mot de passe doit contenir au moins une lettre majuscule ou minuscule'
