module('measure tool')

test("unit conversions", 22, function(){
    measureTool = new lingcod.measureTool()
    
    // metric tests
    measureTool.setUnits('metric');
    
    test_vals = measureTool.convertMetricValue( 'area', 1 );
    equals(test_vals[0], 1);
    equals(test_vals[1], 'sq m');
    
    test_vals = measureTool.convertMetricValue( 'distance', 1 );
    equals(test_vals[0], 1);
    equals(test_vals[1], 'm');
    
    test_vals = measureTool.convertMetricValue( 'area', 1000000 );
    equals(test_vals[0], 1);
    equals(test_vals[1], 'sq km');
    
    test_vals = measureTool.convertMetricValue( 'distance', 1000 );
    equals(test_vals[0], 1);
    equals(test_vals[1], 'km');
    
    // english tests
    measureTool.setUnits('english');
    
    test_vals = measureTool.convertMetricValue( 'area', 1000 );
    equals(test_vals[0], 10763.9104 );
    equals(test_vals[1], 'sq ft' );
    
    test_vals = measureTool.convertMetricValue( 'area', 1000000 );
    equals(test_vals[0], 0.386102159 );
    equals(test_vals[1], 'sq mi' );
    
    test_vals = measureTool.convertMetricValue( 'distance', 0.5 );
    equals(test_vals[0], 1.64041995 );
    equals(test_vals[1], 'ft' );
    
    test_vals = measureTool.convertMetricValue( 'distance', 1000 );
    equals(test_vals[0], 0.621371192 );
    equals(test_vals[1], 'mi' );
    
    // nautical tests
    measureTool.setUnits('nautical');
    
    test_vals = measureTool.convertMetricValue( 'area', 1000000 );
    equals(test_vals[0], 0.29155335 );
    equals(test_vals[1], 'sq naut mi' );
    
    test_vals = measureTool.convertMetricValue( 'distance', 500 );
    equals(test_vals[0], 0.2699784015 );
    equals(test_vals[1], 'naut mi' );
    
    // error test
    measureTool.setUnits('bogus');
    test_vals = measureTool.convertMetricValue( 'area', 1000000 );
    equals(test_vals[0], 0 );
    equals(test_vals[1], 'invalid units set' );
});