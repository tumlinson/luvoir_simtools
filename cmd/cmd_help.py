

def help(): 
   return """
        <left> 
        <p> This tool illustrates color magnitudes for LUVOIR and other telescopes like it. For now, the "color" is F814W and F606W, and the "magnitude" is F814W. 
        <p> In the "Stars" tab you can set the age, metallcity, distance, and apparent surface brightness of the model population. The tool 
            generates a sample of 10,000 stars with the specified parameters and displays the resulting CMD. 
        <p> In the "Exposure" tab you can set the telescope aperture, exposure time (per band), and the S/N of the floating label at right. 
        <p> The underlying CMDs are drawn from Charlie Conroy's FSPS code, using a simple stellar population with a Chabrier IMF. 
            The blue magnitude numbers at right are the apparent magnitudes in F814W at the distance given in the slider. The apparent magnitude 
            corresponding to the selected distance is given in light blue, and the computed photometric S/N is given in red. You can tune the 
            telescope, exposure, and desired S/N to estimate depths for photometric limits. For the default population (Age = 10 Gyr, solar metallicity, 
            D = 1 Mpc, and AB = 20 / sq. arcsec, S/N = 10 is achieved at AB = 30.9 in 1 hour per band. S/N = 100 is obtained at F814W = 27.6 ABmag in 1 hour. 
            These values are reachable in the no-crowding limit. 
        <p> CMDs are often needed in crowding-limited regions, so this tool estimates the number of stars per square arcsecond to derive crowding 
	    limits independently of the photometric limits. The number of stars per square arcsecond at which "good" photometry can be obtained 
	    is scaled by aperture as 10 * (D/2.4)^2 from the PHAT data of Dalcanton et al. At AB = 22 mag / arcsec^2, the crowding limit is ~390 stars 
	    per arcsec^2 and lies at about AB 30.2 for the population mentioned above. 
        <p> Note that in this beta version of the tool, the noise in the CMD is not scaled for each exposure, and so is illustrative only. 
            The magnitudes and S/N ratios are computed directly from the LUVOIR HDI ETC. 
        </left> 
          """

