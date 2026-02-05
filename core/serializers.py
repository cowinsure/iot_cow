from rest_framework import serializers
from .models import Profile, Cow


class ProfileSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'

    def get_image_url(self, obj):
        request = self.context.get('request') if hasattr(self, 'context') else None
        if obj.image and hasattr(obj.image, 'url'):
            url = obj.image.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class CowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cow
        fields = '__all__'
        read_only_fields = ('timestamp',)
