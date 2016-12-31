

def help(): 
   return """

        <div> 
          <p>This is a basic presentation of simulated spectra for several types of astrophysical objects. </p>
          <p>The underlying model for O/NIRS is derived from the python-based version of Tyler Robinson's coronagraphic spectrum and noise model (Robinson et al. 2016). Python by Jacob Lustig-Yaeger and O/NIRS development by Giada Arney. Bokeh rendering by Jason Tumlinson and Giada Arney. </p>
          <p>The "Target" tab includes options to simulate several types of astrophysical object spectra that can be selected from the "Object Spectrum" dropdown menu. The log telescope-planetary system separation distance can be set using the "Distance" slider. When a target is selected, the "Log Object Radius" slider will default to the correct position for the selected target. <br><Br>
              
              The "Observation" tab includes sliders for telescope integration time per coronagraphic bandpass, mirror diameter, spectrograph resolution, telescope temperature, the maximum length of time of a single exposure, and the option to turn on a ground-based simulator.<br><Br>
            
       In the "Download" tab, spectral data can be downloaded in either .txt or .fits format.<br><br>

        For full details, please see the readme file <a href="http://jt-astro.science/luvoir_simtools/onirs_model/onirs_readme.txt" target="_blank">here</a>.
        </div>




          """

