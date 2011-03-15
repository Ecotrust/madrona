var doc = {
  "generic-links": [
    {
      "title": "Copy", 
      "models": [
        "layers_privatelayerlist", 
        "layers_privatesuperoverlay", 
        "mlpa_mpa", 
        "mlpa_array", 
        "mlpa_shipwreck", 
        "mlpa_pipeline", 
        "mlpa_folder"
      ], 
      "uri-template": "/features/generic-links/links/copy/{id+}/", 
      "rel": "edit", 
      "method": "POST", 
      "select": "multiple single"
    }, 
    {
      "models": [
        "layers_privatelayerlist", 
        "layers_privatesuperoverlay", 
        "mlpa_mpa", 
        "mlpa_array", 
        "mlpa_shipwreck", 
        "mlpa_pipeline", 
        "mlpa_folder"
      ], 
      "uri-template": "/features/generic-links/links/kml/{id+}/", 
      "select": "multiple single", 
      "rel": "alternate", 
      "title": "KML"
    }
  ], 
  "feature-classes": [
    {
      "link-relations": {
        "self": {
          "title": 'Attributes',
          "uri-template": "/features/shipwreck/{id}/"
        }, 
        "create": {
          "uri-template": "/features/shipwreck/form/"
        }, 
        "edit": [
            {
              "title": "Attributes and Geometry",
              "uri-template": "/features/shipwreck/{id}/form/"
            }
        ]
      }, 
      "id": "mlpa_shipwreck", 
      "title": "Shipwreck"
    }, 
    {
      "link-relations": {
        "self": {
        "title": 'Attributes',
            
          "uri-template": "/features/mpa/{id}/"
        }, 
        "create": {
          "uri-template": "/features/mpa/form/"
        }, 
        "edit": [
            {
              "title": "Attributes and Geometry",
              "uri-template": "/features/mpa/{id}/form/"
            }
        ]
      }, 
      "id": "mlpa_mpa", 
      "title": "Marine Protected Area"
    }, 
    {
      "link-relations": {
        "self": {
            "title": 'Attributes',
            
          "uri-template": "/features/array/{id}/"
        }, 
        "create": {
          "uri-template": "/features/array/form/"
        }, 
        "edit": [
            {
              "title": "Attributes and Geometry",
              "uri-template": "/features/array/{id}/form/"
            }
        ]
      }, 
      "id": "mlpa_array", 
      "title": "Array"
    }, 
    {
      "link-relations": {
        "self": {
            "title": 'Attributes',
            
          "uri-template": "/features/pipeline/{id}/"
        }, 
        "create": {
          "uri-template": "/features/pipeline/form/"
        }, 
        "edit": [
            {
              "title": "Attributes and Geometry",
              "uri-template": "/features/pipeline/{id}/form/"
            }
        ]
      }, 
      "id": "mlpa_pipeline", 
      "title": "Pipeline"
    }
  ]
};