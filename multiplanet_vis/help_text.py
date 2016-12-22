

def help(): 
   return """
          <p> This tool visualizes the results of detailed exoplanet 
          mission yield simulations described in Stark et al. (2014), 
          ApJ, 795, 122 and Stark et al. (2015), ApJ, 808, 149. The 
          python code to render the results was written by Jason 
          Tumlinson. The planet classification and boundaries are 
          from Kopparapu et al. (in prep). <br> 
               
          <p> The histogram plot at upper left shows various exoplanet 
          categories (rocky, Neptune and Jupiter-size planets from 
          left to right) and the corresponding yield numbers for 
          different incident stellar fluxes (colored histograms) 
          where the colors represent the threshold stellar flux at 
          which metals (red), water-vapor (green) and carbon dioxide
          (blue) condense in the respective planetary atmospheres. 
          For this analysis, the fraction of stars with an exoplanet 
          candidate (eta_rocky, eta_Neptune and eta_Jupiter) is 
          calculated from Petigura et al.(2013) dataset. The planets
          are observed over 1 year of total exposure time using 
          high-contrast optical imaging with a coronagraph. At least 
          one imaging observation of every star is performed to 
          find the exoplanet candidates. The telescope aperture and 
          coronagraph contrast can be varied with the slider bars. 

          <p> The plot on the right shows the real host stars 
          (colored dots) surveyed to find those planets. The Sun 
          is at the center. The Hover Tool shows each star's name, 
          parameters, and total completeness for Earths. 
          The color of the 
          dot indicates the chance of detecting an exoEarth around 
          that star if it is present. 
          """

