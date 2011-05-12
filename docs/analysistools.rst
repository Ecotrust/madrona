`lingcod.analysistools`
=================================

The analysistools module provides a toolkit to standardize interaction with external modeling/analysis software.

Eventually this will include:

* The 'Analysis' abstract base class; an API for instance properties/methods
* JS widgets
* Model and Form Fields
* Validation
* Form generation/metaclass 
* KML representaiton 
* Standard ways of handling asyncronous procedures
* Default templates for input/output parameters
* A Library of common bridge protocols (GRASS, starspan, Marxan, etc)

Currently, it is in a very 'alpha' stage and will be rapidly evolving over the course of 2011. 

When to use an Analysis feature
-------------------------------
If your feature does not take a user-input geometry (only input parameters) and/or requires some significant processing on the server in order to populate certain fields (geometry or otherwise), then you could probably benefit from the analysistools goodies. 

Basics
------
Here is a barebones Analysis feature. Notice that the input_ and output_ field names are significant; the user will provide the inputs and the run() method (called when the feature save() method is fired off) which will take the input parameters and populate the output fields::

    from lingcod.analysistools.models import Analysis

    class SumABAnalysis(Analysis):
        input_a = models.IntegerField()
        input_b = models.IntegerField()
        output_sum = models.IntegerField(blank=True, null=True)

        def run(self):
            self.output_sum = self.input_a + self.input_b

The save() method takes a rerun=True/False boolean kwarg so you can override the save() method to only call run() when appropriate. 

There is also a .done property (is the async process completed?) and kml_working and kml_done properties to specify the kml representation in the case that the async process is still running or is completed. 
