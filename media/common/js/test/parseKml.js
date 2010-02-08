(function(){
    
    var simpleKml = '<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom"><Document><name>KmlFile</name><Style id="sn_ylw-pushpin">	<IconStyle>		<scale>1.1</scale>		<Icon>				<href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>			</Icon>			<hotSpot x="20" y="2" xunits="pixels" yunits="pixels"/>		</IconStyle>	</Style>	<StyleMap id="msn_ylw-pushpin">		<Pair>			<key>normal</key>			<styleUrl>#sn_ylw-pushpin</styleUrl>		</Pair>		<Pair>			<key>highlight</key>			<styleUrl>#sh_ylw-pushpin</styleUrl>		</Pair>	</StyleMap>	<Style id="sh_ylw-pushpin">		<IconStyle>			<scale>1.3</scale>			<Icon>				<href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>			</Icon>			<hotSpot x="20" y="2" xunits="pixels" yunits="pixels"/>		</IconStyle>	</Style>	<Placemark>		<name>test</name>		<LookAt>			<longitude>-124.1159130026133</longitude>			<latitude>41.1825121392081</latitude>			<altitude>0</altitude>			<range>9665.412752509426</range>			<tilt>0</tilt>			<heading>-1.510372901580287e-08</heading>			<altitudeMode>relativeToGround</altitudeMode>			<gx:altitudeMode>relativeToSeaFloor</gx:altitudeMode>		</LookAt>		<styleUrl>#msn_ylw-pushpin</styleUrl>		<Point>			<coordinates>-124.1159130026132,41.1825121392081,0</coordinates>		</Point>	</Placemark></Document></kml>';
    var complexAtomLinks = '<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:mm="http://marinemap.org"><Document>	<name>Marine Protected Areas and Arrays</name>	<visibility>0</visibility>	<open>1</open>	<atom:link rel="marinemap.create_form" title="Marine Protected Area" mm:icon="/path/to/icon.png" mm:model="mlpa_mlpampa" href="/mpas/form/"></atom:link><atom:link rel="marinemap.create_form" title="Array" mm:icon="/path/to/icon.png" mm:model="mlpa_mpaarray" href="/arrays/form/"></atom:link>	<Style id="SMCA-style">		<IconStyle>			<color>01000000</color>			<scale>0.7</scale>			<Icon>				<href>http://maps.google.com/mapfiles/kml/paddle/wht-blank.png</href>			</Icon>		</IconStyle>		<LabelStyle>			<scale>0.7</scale>		</LabelStyle>		<BalloonStyle>			<text><![CDATA[<font color="#1A3752"><strong>$[name]</strong></font><br />            <font size=1>$[designation]</font><br />            <font size=1>Created by $[user] on $[modified]</font>]]></text>			<bgColor>ffeeeeee</bgColor>		</BalloonStyle>		<LineStyle>		</LineStyle>		<PolyStyle>			<color>77a80700</color>		</PolyStyle>	</Style>	<Style id="SMCA-style0">		<IconStyle>			<color>01000000</color>			<scale>0.7</scale>			<Icon>				<href>http://maps.google.com/mapfiles/kml/paddle/wht-blank.png</href>			</Icon>		</IconStyle>		<LabelStyle>			<scale>0.7</scale>		</LabelStyle>		<BalloonStyle>			<text><![CDATA[<font color="#1A3752"><strong>$[name]</strong></font><br />            <font size=1>$[designation]</font><br />            <font size=1>Created by $[user] on $[modified]</font>]]></text>			<bgColor>ffeeeeee</bgColor>		</BalloonStyle>		<LineStyle>		</LineStyle>		<PolyStyle>			<color>77a80700</color>		</PolyStyle>	</Style>	<Style id="SMP-style">		<IconStyle>			<color>01000000</color>			<scale>0.7</scale>			<Icon>				<href>http://maps.google.com/mapfiles/kml/paddle/wht-blank.png</href>			</Icon>		</IconStyle>		<LabelStyle>			<scale>0.7</scale>		</LabelStyle>		<BalloonStyle>			<text><![CDATA[<font color="#1A3752"><strong>$[name]</strong></font><br />            <font size=1>$[designation]</font><br />            <font size=1>Created by $[user] on $[modified]</font>]]></text>			<bgColor>ffeeeeee</bgColor>		</BalloonStyle>		<LineStyle>		</LineStyle>		<PolyStyle>			<color>77ffff00</color>		</PolyStyle>	</Style>	<Style id="defaultstyle">		<IconStyle>			<color>01000000</color>			<scale>0.7</scale>			<Icon>				<href>http://maps.google.com/mapfiles/kml/paddle/wht-blank.png</href>			</Icon>		</IconStyle>		<LabelStyle>			<scale>0.7</scale>		</LabelStyle>		<BalloonStyle>			<text><![CDATA[<font color="#1A3752"><strong>$[name]</strong></font><br />            <font size=1>no designation</font><br />            <font size=1>Created by $[user] on $[modified]</font>]]></text>			<bgColor>ffeeeeee</bgColor>		</BalloonStyle>		<LineStyle>		</LineStyle>		<PolyStyle>			<color>778b1a55</color>		</PolyStyle>	</Style>	<Style id="SMR-style">		<IconStyle>			<color>01000000</color>			<scale>0.7</scale>			<Icon>				<href>http://maps.google.com/mapfiles/kml/paddle/wht-blank.png</href>			</Icon>		</IconStyle>		<LabelStyle>			<scale>0.7</scale>		</LabelStyle>		<BalloonStyle>			<text><![CDATA[<font color="#1A3752"><strong>$[name]</strong></font><br />            <font size=1>$[designation]</font><br />            <font size=1>Created by $[user] on $[modified]</font>]]></text>			<bgColor>ffeeeeee</bgColor>		</BalloonStyle>		<LineStyle>		</LineStyle>		<PolyStyle>			<color>770000ff</color>		</PolyStyle>	</Style>	<Placemark id="/mpas/5/">		<name>test from chad</name>		<visibility>0</visibility>		<styleUrl>#SMCA-style</styleUrl>		<Style>			<ListStyle>				<listItemType>check</listItemType>				<ItemIcon>					<state>open closed</state>					<href>http://marinemap.googlecode.com/svn/trunk/media/common/images/silk/shape_square.png</href>				</ItemIcon>				<bgColor>00ffffff</bgColor>				<maxSnippetLines>2</maxSnippetLines>			</ListStyle>		</Style>		<ExtendedData>			<Data name="mpaid">				<value>5</value>			</Data>			<Data name="name">				<value>test from chad</value>			</Data>			<Data name="user">				<value>cburt</value>			</Data>			<Data name="created">				<value>2010-01-29 13:25:33.329139</value>			</Data>			<Data name="modified">				<value>Feb 06,2010</value>			</Data>			<Data name="area">				<value>92178199.3424</value>			</Data>			<Data name="designation">				<value>(SMCA) State Marine Conservation Area</value>			</Data>		</ExtendedData>		<MultiGeometry>			<Point>				<coordinates>-124.111992519,41.4953972394,0</coordinates>			</Point>			<Polygon>				<extrude>1</extrude>				<altitudeMode>absolute</altitudeMode>				<outerBoundaryIs>					<LinearRing>						<coordinates>-124.1844439710667,41.55965991388442,100 -124.1816691864836,41.55544754291388,100 -124.1781313186958,41.55118094281812,100 -124.1760072639605,41.54328514950828,100 -124.1741601138125,41.53914756236303,100 -124.1718402687297,41.53514662711406,100 -124.1665321804958,41.52838560920042,100 -124.1602906210431,41.5226510274936,100 -124.1578379147454,41.51574544420325,100 -124.1542803931734,41.5094361098426,100 -124.1530997903464,41.50448467234733,100 -124.1515442530813,41.50028010644892,100 -124.1476504468869,41.49319066634348,100 -124.1456874906715,41.48803279768533,100 -124.1427995596302,41.48273768545742,100 -124.1386430125235,41.46996683709871,100 -124.1357848520922,41.46396148610554,100 -124.1352422402295,41.46094429267571,100 -124.1352604105106,41.45106958956075,100 -124.1349018720806,41.44671373926634,100 -124.1333060641194,41.43916255365195,100 -124.1319520033391,41.43493047649422,100 -124.0640979337965,41.4288894802561,100 -124.0641452952298,41.43148328356313,100 -124.0629967847504,41.44080289038444,100 -124.0641152878476,41.44696720990554,100 -124.066274718597,41.452022892523,100 -124.0657573702398,41.45554955545381,100 -124.0658797746831,41.46215984798877,100 -124.0647765874006,41.46353935312116,100 -124.0651481462792,41.46358432157379,100 -124.0660627845445,41.47025567607491,100 -124.0679496943583,41.47520131182488,100 -124.0684364518975,41.47556603188936,100 -124.068406097608,41.47853879120017,100 -124.0689226311478,41.47915552231965,100 -124.0694706650953,41.48151499854204,100 -124.0706572998122,41.48256664056376,100 -124.0713005653644,41.483721833837,100 -124.0714909279592,41.48716815400135,100 -124.07249738371,41.49089153139245,100 -124.0732228412533,41.49206137512876,100 -124.0753150311971,41.49407063537829,100 -124.0748362164705,41.49661944944057,100 -124.0759225009234,41.50175713952605,100 -124.0770135340653,41.50309244205802,100 -124.0777857967762,41.50652755453518,100 -124.0787237300525,41.50727020602386,100 -124.0791109967483,41.50824839278653,100 -124.0804178995675,41.50889272791027,100 -124.0810974375116,41.50987810726879,100 -124.0817389139965,41.51605548836056,100 -124.0817411276882,41.52259912585367,100 -124.0830298463779,41.52408423758141,100 -124.0846332882324,41.52429237601482,100 -124.0841161485977,41.52483758370788,100 -124.0831912788343,41.52482431786304,100 -124.0828980232264,41.52513729438662,100 -124.0826594934958,41.52944150803537,100 -124.0811760336458,41.53026538372906,100 -124.0879508006456,41.55114475345153,100 -124.0889975276007,41.55128044024539,100 -124.090465936794,41.55301715798321,100 -124.0922200917285,41.55315292437729,100 -124.092060088545,41.55342818155165,100 -124.093609395772,41.55544267834236,100 -124.0933911338071,41.55587568913015,100 -124.0936964593842,41.55674461853138,100 -124.0944993591689,41.55812632786601,100 -124.0949063248407,41.55817962694252,100 -124.0953022457663,41.55974695925964,100 -124.096402802939,41.5604215997048,100 -124.0957397640135,41.56085226544266,100 -124.0958679795249,41.56190499853714,100 -124.1844439710667,41.55965991388442,100 </coordinates>					</LinearRing>				</outerBoundaryIs>			</Polygon>		</MultiGeometry>		<atom:link rel="marinemap.update_form" title="Edit" mm:icon="/path/to/icon.jpg" mm:model="mlpa_mlpampa" href="/mpas/5/form/"></atom:link><atom:link rel="marinemap.share_form" title="Share" mm:icon="/path/to/icon.jpg" mm:model="mlpa_mlpampa" href="/sharing/51/5/"></atom:link><atom:link rel="marinemap.copy" title="Copy" mm:icon="/path/to/icon.jpg" mm:model="mlpa_mlpampa" href="/mpas/5/copy/"></atom:link><atom:link rel="self" title="test from chad" mm:model="mlpa_mlpampa" mm:pk="5" href="/mpas/5/"></atom:link><atom:link rel="alt" href="/kml/f8a627b0f02cbacea8d150fe54b2107b/5/mpa.kmz" title="as kmz (Google Earth)" type="application/vnd.google-earth.kmz"></atom:link><atom:link rel="alt" href="" title="as shapefile" type="application/shapefile"></atom:link>	</Placemark></Document></kml>';
    
    module('parseKml');
    
    test('parsing a simple document', function(){
        var kml = lingcod.parseKml(simpleKml);
        ok(kml);
        equals(kml.find('Placemark').length, 1);
    });

    test('parsing a complex document with atom links', function(){
        var kml = lingcod.parseKml(complexAtomLinks);
        ok(kml);
        equals(kml.find('Placemark').length, 1);
        equals(kml.findLinks().length, 8);
        equals(kml.findLinks({rel: 'self'}).length, 1);
    });
    
})();
