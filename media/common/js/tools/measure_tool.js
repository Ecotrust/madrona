/**
* Unit conversion table used by measureTool to convert metric units to others,
* and to select appropriate units based on size of value.
*/
lingcod.measureConvTable = [
    [ 'metric', 
        [ // distance measures
            ['m', 1, 500 ], // switch to km at 1/2 km
            ['km', 0.001, null ]
        ],
        [ // area measures
            ['sq m', 1, 100000 ], // switch to sq km at 1/10 sq km
            ['sq km', 0.000001, null ]
        ]
    ],
    [ 'english', 
        [ // distance measures
            ['ft', 3.2808399, 0.9144 ], // switch to yards at 1 yd
            //['yd', 1.0936133, 804.672 ], // switch to miles at 1/2 mile
            ['mi', 0.000621371192, null ]
        ],
        [ // area measures
            ['sq ft', 10.7639104, 25899.8811 ], // switch to sq miles at 0.01 sq miles
            //['sq yd', 1.19599005, 1294994.06 ], // switch to sq miles at 1/2 sq mile
            ['sq mi', 0.000000386102159, null ]
        ]
    ],
    [ 'nautical', 
        [ // distance measures
            ['naut mi', 0.000539956803, null ]
        ],
        [ // area measures
            ['sq naut mi', 0.00000029155335, null ]
        ]
    ]
];

/**
 * Creates a new measurement tool.
 *    
 * @constructor
 */
lingcod.measureTool = function() {
    this.placemark = null;
    this.distTarget = null;
    this.areaTarget = null;
    this.gex = null;
    this.area = 0.0;
    this.distance = 0.0;
    this.units = 'metric';
    this.area_unit = 'sq m';
    this.distance_unit = 'm';
};

lingcod.measureTool.prototype.clear = function() 
{ 
    this.area = 0.0;
    this.distance = 0.0;
    
    if ( this.placemark )
    {
        if ( this.distTarget )
        {
            this.gex.edit.endEditLineString( this.placemark.getGeometry() );
            document.getElementById(this.distTarget).innerHTML = 'N/A';
            this.distTarget = null;
        }
        
        if ( this.areaTarget )
        { 
            this.gex.edit.endEditLineString( this.placemark.getGeometry().getOuterBoundary() );
            document.getElementById(this.areaTarget).innerHTML = 'N/A';
            this.areaTarget = null;
        }
    
        this.gex.dom.removeObject( this.placemark );
        this.placemark = null;
    }
};

/**
 * Set the measure tool's system of measurement for reporting (still uses metric internally)
 * @param {String} units The name of the system of measure, i.e. 'english', 'metric', 'nautical'
 */
lingcod.measureTool.prototype.setUnits = function( units ) {
    this.units = units;
    this.updateDistance();
};

/**
 * Start accepting user input for shape-draw. Sets callbacks to keep measures updated and to switch to edit mode on completion.
 * @param {GEarthExtensions} gex The handle to the GEarthExtensions object
 * @param {String} areaSpanId The id of an HTML tag whose innerHTML will be overwritten with measure results.
 */
lingcod.measureTool.prototype.measureArea = function( gex, areaSpanId ) 
{
    var self = this;
    this.gex = gex;
    
    this.clear();

    this.areaTarget = areaSpanId;

    this.placemark = gex.dom.addPlacemark({
        polygon: [],
        style: {
            line: { width: 2, color: '#ff0' },
            poly: { color: '8000ffff' }
        }
    });
    
    var drawLineStringOptions = {
        bounce: false,
        drawCallback: function() {
            self.updateDistance();
        },
        finishCallback: function() {
            var editLineStringOptions = {
                editCallback: function() {
                    self.updateDistance();
                }
            }
            gex.edit.editLineString( self.placemark.getGeometry().getOuterBoundary(), editLineStringOptions );
        }
    };

    gex.edit.drawLineString( this.placemark.getGeometry().getOuterBoundary(), drawLineStringOptions );
};

/**
 * Start accepting user input for line-draw. Sets callbacks to keep measures updated and to switch to edit mode on completion.
 * @param {GEarthExtensions} gex The handle to the GEarthExtensions object
 * @param {String} distSpanId The id of an HTML tag whose innerHTML will be overwritten with measure results.
 */
lingcod.measureTool.prototype.measureDistance = function( gex, distSpanId ) 
{    
    var self = this;
    this.gex = gex;
    
    this.clear();
    
    this.distTarget = distSpanId;

    this.placemark = gex.dom.addPlacemark({
        lineString: [],
        style: {
            line: { width: 2, color: '#ff0' }
        }
    });
    
    var drawLineStringOptions = {
        bounce: false,
        drawCallback: function() {
            self.updateDistance();
        },
        finishCallback: function() {
            var editLineStringOptions = {
                editCallback: function() {
                    self.updateDistance();
                }
            }
            gex.edit.editLineString( self.placemark.getGeometry(), editLineStringOptions );
        }
    };

    gex.edit.drawLineString( this.placemark.getGeometry(), drawLineStringOptions );
};


/**
 * Start accepting user input for shape-draw. Sets callbacks to keep measures updated and to switch to edit mode on completion.
 * @param {String} measure_type_str 'distance' or 'area' (assumes 'distance' if not 'area')
 * @param {Number} value The metric value to convert to the measureTool's currently set units.
 * @return [{Number}, {String}] The converted value and its units.
 */
lingcod.measureTool.prototype.convertMetricValue = function( measure_type_str, value )
{
    var SYSTEM = 0;
    var DISTANCE_MAPPINGS = 1;
    var AREA_MAPPINGS = 2;
    
    var UNIT = 0;
    var CONVERSION_FACTOR = 1;
    var RANGE_MAX = 2;
    
    var measure_type = DISTANCE_MAPPINGS;
    if ( measure_type_str == 'area' )
        measure_type = AREA_MAPPINGS;
    
    for ( var system_iter = 0; system_iter < lingcod.measureConvTable.length; system_iter++ )
    {
        if ( lingcod.measureConvTable[system_iter][SYSTEM] == this.units )
        {
            for ( var unit_iter = 0; unit_iter < lingcod.measureConvTable[system_iter][measure_type].length; unit_iter++ )
            {
                if ( value < lingcod.measureConvTable[system_iter][measure_type][unit_iter][RANGE_MAX] 
                    || lingcod.measureConvTable[system_iter][measure_type][unit_iter][RANGE_MAX] == null )
                    return [ value * 
                            lingcod.measureConvTable[system_iter][measure_type][unit_iter][CONVERSION_FACTOR],
                        lingcod.measureConvTable[system_iter][measure_type][unit_iter][UNIT] ];
            }
        }
    }
    
    return[ 0, 'invalid units set' ];
};

/**
 * Calculate the current measurement(s) based on the state of the measureTool's placemark object.
 * Writes values to target HTML object and stores internally.
 */
lingcod.measureTool.prototype.updateDistance = function() 
{ 
    if ( this.areaTarget ) 
    {
        this.area = new geo.Polygon(this.placemark.getGeometry()).area();
        converted_val_n_unit = this.convertMetricValue( 'area', this.area );
        
        this.area = converted_val_n_unit[0];
        this.area_unit = converted_val_n_unit[1];
        
        document.getElementById(this.areaTarget).innerHTML =
            this.area.toFixed(2) + ' ' + this.area_unit;
    }
      
    if ( this.distTarget ) 
    {
        this.distance = new geo.Path(this.placemark.getGeometry()).distance();
        converted_val_n_unit = this.convertMetricValue( 'distance', this.distance );
        
        this.distance = converted_val_n_unit[0];
        this.distance_unit = converted_val_n_unit[1];
        
        document.getElementById(this.distTarget).innerHTML =
            this.distance.toFixed(2) + ' ' + this.distance_unit;
    }
};
