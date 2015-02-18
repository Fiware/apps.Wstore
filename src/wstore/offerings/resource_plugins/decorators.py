# -*- coding: utf-8 -*-

# Copyright (c) 2015 CoNWeT Lab., Universidad Politécnica de Madrid

# This file is part of WStore.

# WStore is free software: you can redistribute it and/or modify
# it under the terms of the European Union Public Licence (EUPL)
# as published by the European Commission, either version 1.1
# of the License, or (at your option) any later version.

# WStore is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# European Union Public Licence for more details.

# You should have received a copy of the European Union Public Licence
# along with WStore.
# If not, see <https://joinup.ec.europa.eu/software/page/eupl/licence-eupl>.


from __future__ import unicode_literals

from wstore.models import ResourcePlugin
from functools import wraps


def load_plugin_module(module):
    module_class_name = module.split('.')[-1]
    module_package = module.partition('.' + module_class_name)[0]

    module_class = getattr(__import__(module_package, globals(), locals(), [module_class_name], -1), module_class_name)

    return module_class


def _get_plugin_model(name):
    try:
        plugin_model = ResourcePlugin.objects.get(name=name)
    except:
        # Validate resource type
        raise ValueError('Invalid request: The specified resource type is not registered')

    return plugin_model


def register_resource_events(func):

    @wraps(func)
    def wrapper(provider, data):
        # Get plugin models
        if data['resource_type'] != 'Downloadable' and data['resource_type'] != 'API':

            plugin_model = _get_plugin_model(data['resource_type'])

            # TODO: Validate formats for API resource
            # Validate format
            if data['link'] != "" and 'URL' not in plugin_model.formats:
                raise ValueError('Invalid plugin format: URL not allowed for the resource type')

            if data['content_path'] != "" and 'FILE' not in plugin_model.formats:
                raise ValueError('Invalid plugin format: File not allowed for the resource type')

            # Validate mime types
            if len(plugin_model.media_types) > 0 and data['content_type'] not in plugin_model.media_types:
                raise ValueError('Invalid media type: ' + data['content_type'] + ' is not allowed for the resource type')

            # Load plugin module
            module_class = load_plugin_module()
            plugin_module = module_class()

            # Call on pre create event handler
            plugin_module.on_pre_create(provider, data)

        # Call method
        func(provider, data)

        # Call on post create event handler
        if data['resource_type'] != 'Downloadable' and data['resource_type'] != 'API':
            plugin_module.on_post_create(provider, data)


def upgrade_resource_events(func):

    @wraps(func)
    def wrapper(resource):

        if resource.resource_type != 'Downloadable' and resource.resource_type != 'API':
            plugin_model = _get_plugin_model(resource.resource_type)

            # TODO: Validate formats for API resource
            # Validate format
            if resource.download_link != "" and 'URL' not in plugin_model.formats:
                raise ValueError('Invalid plugin format: URL not allowed for the resource type')

            if resource.resource_path != "" and 'FILE' not in plugin_model.formats:
                raise ValueError('Invalid plugin format: File not allowed for the resource type')

            # Load plugin module
            module_class = load_plugin_module()
            plugin_module = module_class()

            # Call on pre create event handler
            plugin_module.on_pre_create(resource)

        # Call method
        func(resource)

        # Call on post create event handler
        if resource.resource_type != 'Downloadable' and resource.resource_type != 'API':
            plugin_module.on_post_create(resource)


def update_resource_events(func):
    pass