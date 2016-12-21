

def help(): 
   return """
          <h2> 
          This tool visualizes the results of detailed exoplanet <br> 
          mission yield simulations described in Stark et al. (2014), <br> 
          ApJ, 795, 122 and Stark et al. (2015), ApJ, 808, 149. The <br> 
          python code to render the results was written by Jason <br> 
          Tumlinson. The planet classification and boundaries are <br> 
          from Kopparapu et al. (in prep). <br> 
          <br> 
          The histogram plot on the left shows various exoplanet <br> 
          categories (rocky, Neptune and Jupiter-size planets from <br> 
          left to right) and the corresponding yield numbers for <br> 
          different incident stellar fluxes (colored histograms) <br> 
          where the colors represent the threshold stellar flux at <br> 
          which metals (red), water-vapor (green) and carbon dioxide <br> 
          (blue) condense in the respective planetary atmospheres. <br> 
          For this analysis, the fraction of stars with an exoplanet <br> 
          candidate (eta_rocky, eta_Neptune and eta_Jupiter) is <br> 
          calculated from Petigura et al.(2013) dataset. The planets <br> 
          are observed over 1 year of total exposure time using <br> 
          high-contrast optical imaging with a coronagraph. At least <br> 
          one imaging observation of every star is performed to <br> 
          find the exoplanet candidates. The telescope aperture and <br> 
          coronagraph contrast can be varied with the slider bars. <br> 
          <br> 
          The main plot on the right shows the real host stars <br> 
          (colored dots) surveyed to find those planets. The Sun <br> 
          is at the center hovering the cursor over a dot will <br> 
          reveal the star name and parameters). The color of the <br> 
          dot indicates the chance of detecting an exoEarth around <br> 
          that star if it is present. <br> 
          """

