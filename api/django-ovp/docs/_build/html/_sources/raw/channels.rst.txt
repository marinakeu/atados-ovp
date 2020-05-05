channels are an important concept and therefore somethings must be taken into account when creating viewsets

= what is a channel? =
ovp can be implemented as a saas structure built into a single database. this essentially means a api should be able serve multiple different websites based on the concept of channels.
By default there's only a single channel and all requests are redirected to this channel, this is the channel 'default'.

There are 3 use cases for channels:
* Season events/campaings such as "children days"/"good deeds day"
* Partners who are hosted inside your main site
* Multi-site hosting

for this channels offer several features such as:
* per channel users
* per channel permissions
* channel autojoin
* cors



= creating and retrieving objects =
There two things that make channels possible. ChannelMiddleware. This middleware populates the request object with a list 



models
All models should extend from ChannelRelationship. This will create an M2M field from the model to the channels


channel permissions


autojoin vs noautojoin


channel cors
A channel can specify its own cors settings. This a
add cors headers middleware



= how to specify a channel? =
You can specify the channel you are working with by setting a header on your request
X-OVP-Channel: default

Your requests can also specify multiple channels, such as
X-OVP-Channel: default;channel1

= Create vs retrieve =
You can specify multiple channels when retrieving objects but you can't specify multiple channels when creating objects (???)



pitfalls
If you're going to modify the object manager, extend it fron ChannelRelationshipManager instead of models.Manager
If you're overriding a serializer create method, you need to pass the channels object like so
obj = Model.objects.create(\*args, \*\*kwargs, object_channel="list")
or
obj = Model(\*args, \*\*kwargs)
obj.save(object_channel="list")

but ideally you wont do that
normally you will extend ChannelRelationshipSerializer and use
obj = super(CustomSerializer, self).create(validated_data)

Viewsets must be decorated
Model should extend ChannelRelationship
Createmodelmixin and channelrelationship should come before other objects on the hierarchy


avoid doing things manually:
self.get_queryset instead of Model.objects or self.queryset
serializer.create() instead of model.create()


don't use force authenticate if you're testing different channels

avoid using unique on channel model, instead use unique_together (field, channel)


channel settings model

