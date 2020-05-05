from rest_framework import serializers

####################
# Token view       #
####################


class RequestTokenViewSerializer(serializers.Serializer):
    client_id = serializers.CharField()
    client_secret = serializers.CharField()
    grant_type = serializers.ChoiceField(choices=["password"])
    email = serializers.CharField()
    password = serializers.CharField()


class ResponseTokenViewSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=False)
    expires_in = serializers.IntegerField(required=False)
    token_type = serializers.CharField(required=False)
    scope = serializers.CharField(required=False)
    refresh_token = serializers.CharField(required=False)


######################
# Convert Token view #
######################
class RequestConvertTokenViewSerializer(serializers.Serializer):
    client_id = serializers.CharField()
    client_secret = serializers.CharField()
    grant_type = serializers.ChoiceField(choices=["convert_token"])
    token = serializers.CharField()


class ResponseConvertTokenViewSerializer(ResponseTokenViewSerializer):
    pass


######################
# Revoke Token view  #
######################
class RequestRevokeTokenViewSerializer(serializers.Serializer):
    client_id = serializers.CharField()
    client_secret = serializers.CharField()
    token = serializers.CharField()
