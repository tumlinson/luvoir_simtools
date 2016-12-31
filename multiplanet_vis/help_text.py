def help(): 
   return """

    <p>This tool visualizes the results of detailed exoplanet
    mission yield simulations, calculated useng the planet
    classifications from Kopparapu et al. (in preparation). The
    methodology is described in Stark et al. (2014), ApJ, 795,
    122 and Stark et al. (2015), ApJ, 808, 149. The python code
    to render the results was written by Jason Tumlinson.
    
    <p>The main plot on the right shows a blind direct imaging
    survey for habitable planet candidates, defined as rocky
    exoplanets (0.5 - 1.4 R_earth) orbiting in the stars'
    habitable zones. The real host stars observed are shown with
    yellow dots, with the Sun at the center (hovering the cursor
    over a dot will reveal the star name and parameters). The
    shade of the dot indicates the chance of detecting a
    habitable planet candidate around that star if it is
    present. The planets are observed over 1 year of total
    exposure time using high-contrast optical imaging with a
    coronagraph. At least one imaging observation of every star
    is performed to find the habitable planet candidates. For
    every detected planet, a partial spectroscopic
    characterization is executed. The telescope aperture and
    coronagraph contrast can be varied with the slider bars.
    
    <p>Stars for which a habitable planet candidate is observed
    are marked with flashing light blue dots. These are
    randomly drawn given the chances of detecting a
    candidate around that star and assuming that the
    fraction of stars with such planets is given by the
    ExoPAG SAG 13 occurrence rates (as given in the
    "Planets" tab).  Clicking on the "Regenerate Sample of
    Detected Candidates" button at the lower left will redo
    the random drawing, showing that the exact number of
    planets found varies from trial to trial.

    <p>The histogram plot on the left visualizes the total
    scientific impact of the habitable planet candidate
    survey.  The y-axis gives the expected total numbers of
    exoplanets observed (yields), which are also given by
    the numbers above the bars. By "expected", we mean the
    most probable yield after many trials of an identically
    executed survey. Three sizes of exoplanets are shown,
    with their definitions given in the table under the
    "Planets" tab.  For each planet size, three incident
    stellar flux classes are shown: hot (red), warm (green),
    and cold (dark blue). The boundaries between the classes
    correspond to the temperatures where metals, water
    vapor, and carbon dioxide condense in a planet's
    atmosphere. The warm bin corresponds to the optimistic
    habitable zone (Kopparapu et al. 2013, 2014); these
    planets can have water clouds. Therefore, the warm rocky
    planets are habitable planet candidates. Planet
    occurrence rates from ExoPAG SAG 13 were adopted for
    this analysis. The expected total number of habitable
    planet candidates may be different from the number of
    planet host stars marked in the main plot on the right
    (flashing dots), due to the random nature of a single
    survey realization.
	"""
