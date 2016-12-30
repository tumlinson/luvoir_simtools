def help(): 
   return """
	<p> This tool visualizes the results of detailed exoplanet direct-imaging yield
	simulations described in Stark et al. (2014), ApJ, 795, 122 and Stark et
	al. (2015), ApJ, 808, 149. The python/bokeh rendering code is by 
	Jason Tumlinson. The planet classifications and boundaries
	are from Kopparapu et al. (in preparation).

	<p> The main plot on the right shows a blind direct imaging survey for
	exoEarths, defined as Earth-sized exoplanets orbiting in the star's 
	habitable zones. The real host stars observed are shown with colored
	dots, with the Sun at the center (hovering the cursor over a dot will
	reveal the star name and parameters). The shade of the dot indicates the
	chance of detecting an exoEarth around that star if it is present. The
	planets are observed over 1 year of total exposure time using
	high-contrast optical imaging with a coronagraph. At least one imaging
	observation of every star is performed to find the exoEarth candidates.
	For every detected planet, a partial spectroscopic characterization is
	executed. The telescope aperture and coronagraph contrast can be varied
	with the slider bars.

	<p> Stars for which an exoEarth candidate is observed are marked with
	flashing dots. These are randomly drawn given the chances of seeing
	detecting an exoEarth candidate around that star and assuming that the
	fraction of stars with exoEarth candidates (&#951<sub>Earth</sub>) is 10%.  Clicking
	on the "Regenerate the Sample of Detected Earths" button at the lower
	left will redo the random drawing, showing that the exact number of
	exoEarth candidates found varies from trial to trial.

	<p> The histogram plot on the left visualizes the total scientific
	impact of the exoEarth survey. The y-axis gives the expected total
	numbers of exoplanets observed (yields), which are also given by the
	numbers above the bars. By 'expected', we mean the most probable yield
	after many trials of an identically executed survey. Three sizes of
	exoplanets are shown: rocky (0.5 - 1.4 R<sub>&#8853</sub>), Neptune-size (1.4 - 4.0
	R<sub>&#8853</sub>), and Jupiter-size (4.0 - 11.0 R<sub>&#8853</sub>) planets. For each planet
	size, three incident stellar flux classes are shown: hot (red), warm
	(green), and cold (blue). The boundaries between the classes correspond
	to the temperatures where metals, water vapor, and carbon dioxide
	condense in a planet's atmosphere. The warm bin corresponds to the
	optimistic habitable zone (Kopparapu et al.  2013, 2014); these planets
	can have water clouds. For this analysis, the fraction of stars with an
	exoplanet candidate (&#951<sub>Earth</sub>, &#951<sub>Neptune</sub>, and &#951<sub>Jupiter</sub>) is
	calculated from the Petigura et al. (2013) dataset. The expected total
	number of exoEarth candidates may be different from the number of
	exoEarth host stars marked in the main plot on the right (flashing
	dots), due to the random nature of a single survey realization.  
        """
