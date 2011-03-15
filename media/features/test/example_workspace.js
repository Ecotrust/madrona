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
    }, 
    {
      "title": "Remove", 
      "models": [
        "mlpa_array", 
        "mlpa_folder"
      ], 
      "uri-template": "/features/generic-links/links/remove/{id+}/", 
      "rel": "edit", 
      "method": "POST", 
      "select": "multiple single"
    }, 
    {
      "title": "Add", 
      "models": [
        "mlpa_array", 
        "mlpa_folder"
      ], 
      "uri-template": "/features/generic-links/links/add/{id+}/", 
      "rel": "edit", 
      "method": "POST", 
      "select": "multiple single"
    }
  ], 
  "feature-classes": [
    {
      "link-relations": {
        "edit": [
          {
            "uri-template": "/features/shipwreck/{id}/form/", 
            "title": "edit"
          }
        ], 
        "self": {
          "uri-template": "/features/shipwreck/{id}/"
        }, 
        "create": {
          "uri-template": "/features/shipwreck/form/"
        }
      }, 
      "id": "mlpa_shipwreck", 
      "title": "Shipwreck"
    }, 
    {
      "link-relations": {
        "edit": [
          {
            "uri-template": "/features/mpa/{id}/form/", 
            "title": "edit"
          }
        ], 
        "self": {
          "uri-template": "/features/mpa/{id}/"
        }, 
        "create": {
          "uri-template": "/features/mpa/form/"
        }
      }, 
      "id": "mlpa_mpa", 
      "title": "Marine Protected Area"
    }, 
    {
      "link-relations": {
        "edit": [
          {
            "uri-template": "/features/array/{id}/form/", 
            "title": "edit"
          }
        ], 
        "self": {
          "uri-template": "/features/array/{id}/"
        }, 
        "create": {
          "uri-template": "/features/array/form/"
        }
      }, 
      "id": "mlpa_array", 
      "collection": {
        "classes": [
          "mlpa_mpa"
        ]
      }, 
      "title": "Array"
    }, 
    {
      "link-relations": {
        "edit": [
          {
            "uri-template": "/features/pipeline/{id}/form/", 
            "title": "edit"
          }
        ], 
        "self": {
          "uri-template": "/features/pipeline/{id}/"
        }, 
        "create": {
          "uri-template": "/features/pipeline/form/"
        }
      }, 
      "id": "mlpa_pipeline", 
      "title": "Pipeline"
    }, 
    {
      "link-relations": {
        "edit": [
          {
            "uri-template": "/features/folder/{id}/form/", 
            "title": "edit"
          }
        ], 
        "self": {
          "uri-template": "/features/folder/{id}/"
        }, 
        "create": {
          "uri-template": "/features/folder/form/"
        }
      }, 
      "id": "mlpa_folder", 
      "collection": {
        "classes": [
          "mlpa_mpa", 
          "mlpa_array", 
          "mlpa_pipeline", 
          "mlpa_shipwreck", 
          "mlpa_folder"
        ]
      }, 
      "title": "Folder"
    }
  ]
};