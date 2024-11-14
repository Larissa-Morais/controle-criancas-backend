from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Crianca, Responsavel, Controle
from .validators import UsernameValidator, NomeValidator, DataNascimentoValidator, TelefoneValidator

class CriancaSerializer(serializers.ModelSerializer):
    idade = serializers.ReadOnlyField()

    class Meta:
        model = Crianca
        fields = ['id_crianca', 'nome', 'data_nascimento', 'classificacao', 'sala', 'idade', 'foto']


class ResponsavelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Responsavel
        fields = ['id_responsavel', 'nome', 'relacionamento_crianca', 'telefone_responsavel']
        read_only_fields = ['id_responsavel']


class ResponsavelInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Responsavel
        fields = ['nome', 'telefone_responsavel', 'relacionamento_crianca']
        extra_kwags = {'telefone_responsavel': {'validators': [TelefoneValidator]}}


class ControleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Controle
        fields = ['id_checkin', 'status', 'data_horario_checkin', 'data_horario_checkout']
        read_only_fields = ['id_checkin', 'status', 'data_horario_checkin', 'data_horario_checkout']


class LoginUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(validators=[UsernameValidator()])
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def validate(self, data):
        username = data['username']
        password = data['password']

        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuário não existe.")
        
        if not user.check_password(password):
            raise serializers.ValidationError("Senha incorreta!")
        
        return user
    

class CadastroUserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user
    

class CadastroCriancaSerializer(serializers.ModelSerializer):
    responsavel_1 = ResponsavelInfoSerializer()
    responsavel_2 = ResponsavelInfoSerializer(required=False)
    foto = serializers.ImageField(required=False)

    class Meta:
        model = Crianca
        fields = ['nome', 'data_nascimento', 'classificacao', 'sala', 'idade', 'responsavel_1', 'responsavel_2', 'observacao', 'foto']

    def create(self, validated_data):
        responsavel_1_data = validated_data.pop('responsavel_1')
        responsavel_2_data = validated_data.pop('responsavel_2', None)

        crianca = Crianca.objects.create(**validated_data)

        responsavel_1, _ = Responsavel.objects.get_or_create(**responsavel_1_data)
        crianca.responsaveis.add(responsavel_1)

        if responsavel_2_data:
            responsavel_2, _ = Responsavel.objects.get_or_create(**responsavel_2_data)
            crianca.responsaveis.add(responsavel_2)

        return crianca
    

        
