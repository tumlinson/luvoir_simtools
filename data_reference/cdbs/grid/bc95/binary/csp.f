	PROGRAM CSP_GALAXEV

c	Computes spectral energy distribution as a function of time for a
c	Composite Stellar Population (CSP) by performing a convolution integral
c	of the spectral energy distributions for a Single Stellar Population SSP
c	with the chosen Star Formation Rate (SFR).

c	Array declarations
	character ans,name*80,save*80
	include 'SSP_4.dec'
	include 'SSP_13.dec'
	include 'csp.dec'
	real w(imw),h(imw)
	real snr(0:jts),pnr(0:jts),bh(0:jts),sn(0:jts),wd(0:jts),rm(0:jts)
	real bol(0:jts),str(0:jts),sf(0:jts),evf(0:jts),fi(21),fc(21)
	equivalence (fi(1),h(1)), (fc(1),h(22))

c	Check if correct filter file is in use.
	j=ifilter()
	if (j.eq.0) then
		write (6,'(2a)') char(7),'Please assign correct filter file'
		stop
	endif

c	Ask for file name
	save='_'
1	call copyright(6)
2	l=largo(save)
	write (6,'(x,3a,$)') 'IS_GALAXEV SSP sed in file [',save(1:l),'] = '
	read (5,'(a)',end=10) name
	if (largo(name).eq.0) name=save
	iread=0
	if (name.ne.save) iread=1

c	Open input sed file (read agin, tb modified in case of truncated SFR)
c	if (iread.ne.0) then
	   save=name
	   close (1)
	   open (1,file=name,form='unformatted',status='old',err=3)
c	   Read basic parameters from SSP input file
	   read (1) nsteps,(tb(i),i=0,nsteps-1),iseg,
     &	   (xx(i),lm(i),um(i),baux(i),cn(i),cc(i),i=1,iseg),
     &	   totm,totn,avs,jo,tauo,id,tcut
	   if (jo.ne.0) then
	      write (6,'(x,a$)')'File does not contain an SSP. Proceed Y/[N] ? '
	      read (5,'(a)',end=10) ans
	      if (ans.ne.'y'.and.ans.ne.'Y') goto 1
	   endif
c	   Read sed from SSP file
	   write (6,'(2a)') ' Reading file ',name
	   write (6,'(2a)') ' Reading file ',save
	   read (1) inw,(w(i),i=1,inw)
	   do n=0,nsteps-1
	   read (1) inw,(fl(i,n),i=1,inw)
	   enddo
	   write (6,*) inw,' points per record'
	   read (1,end=4) nsteps,(bflx(i),i=0,nsteps-1)
	   read (1) nsteps,(strm(i),i=0,nsteps-1)
	   read (1)
	   read (1) nsteps,(evfl(i),i=0,nsteps-1)
	   read (1) nsteps,(snbr(i),i=0,nsteps-1)
	   read (1) nsteps,(pnbr(i),i=0,nsteps-1)
	   read (1) nsteps,(bhtn(i),i=0,nsteps-1)
	   read (1) nsteps,(sntn(i),i=0,nsteps-1)
	   read (1) nsteps,(wdtn(i),i=0,nsteps-1)
	   read (1) nsteps,(rmtm(i),i=0,nsteps-1)
	   close (1)
c	endif

c	Ask for SFR
4	call SFR_0_B(1)

c	Expand time scale if required
	if ((io.ne.2.and.tcut.lt.20.E9).or.(io.eq.2.and.tcut.gt.2.E9))
     &			 call expand_time_steps(nsteps)
	
c	Ask for output file name. Open files.
	lun=-1
	igw=0
c	if (inw.le.42) then
c		lun=-3
c		igw=1
c	endif
	call name_sed(lun,jun,0,igw,name)

c	Write time scale, IMF, and wavelength scale in output file
	if (inw.gt.42) then
		write (lun) nsteps,(tb(i),i=0,nsteps-1),iseg,
     &		(xx(i),lm(i),um(i),baux(i),cn(i),cc(i),i=1,iseg),
     &		totm,totn,avs,io,tau,id,tau,tau,1.,1.,id,id
		write (lun) inw,(w(i),i=1,inw)
	endif

c	Compute convolution integral, rest frame colors, and write results for CSP
	do n=0,nsteps-1
	call convolve_sed(h,n,bol(n),str(n),evf(n),snr(n),pnr(n),bh(n),sn(n),
     &			  wd(n),rm(n))
	if (inw.gt.42) then
		write (lun) inw,(h(i),i=1,inw)
		sf(n)=sfr(tb(n))
c		standard model colors
		call rf_color(tb(n),w,h,inw,lun,bol(n),str(n),sf(n),evf(n),
     &		snr(n),pnr(n),bh(n),sn(n),wd(n),rm(n))
	else
c		Guy Worthey Spectral indices
c		write (lun+10) inw,fi,fc
c		call gw_indices(tb(n),fi,fc,lun)
	endif
	enddo
	if (inw.gt.42) then
		write (lun) nsteps,(bol(i),i=0,nsteps-1)
		write (lun) nsteps,(str(i),i=0,nsteps-1)
		write (lun) nsteps,( sf(i),i=0,nsteps-1)
		write (lun) nsteps,(evf(i),i=0,nsteps-1)
		write (lun) nsteps,(snr(i),i=0,nsteps-1)
		write (lun) nsteps,(pnr(i),i=0,nsteps-1)
		write (lun) nsteps,( bh(i),i=0,nsteps-1)
		write (lun) nsteps,( sn(i),i=0,nsteps-1)
		write (lun) nsteps,( wd(i),i=0,nsteps-1)
		write (lun) nsteps,( rm(i),i=0,nsteps-1)
	endif
	goto 1
3	write (6,'(x,3a)') char(7),'File not found',char(7)
	goto 2
10	end

	FUNCTION FILTER(I,X,Y,N,Z)

c	Returns flux through I filter. The s.e.d. is Y(X) with N data
c	points. Z is the redshift to be applied to the s.e.d.

	INCLUDE 'filter.dec'
	real LINEAR,xlam(300),flux(300),x(n),y(n)

	filter=0.
	if (i.gt.mxft) return

c	Introduced to allow easy computation of K-correction with
c	routine ~/is/k_correct.f
	if (i.le.0) then
		filter=1.
		return
	endif

	if (iread.eq.0) Call FILTER0
	l=0
	do m=1,np(i)
	xlam(m)=r(m,i,1)
	flux(m)=r(m,i,2)*LINEAR(xlam(m)/(1.+z),x,y,n,l)
c	if (i.eq.5) then
c		write (45,*) i,m,l,xlam(m),flux(m)
c	endif
c	if (i.eq.8) then
c		write (47,*) i,m,l,xlam(m),flux(m)
c	endif
c	if (l.eq.0) goto 1
	enddo
	filter=TRAPZ1(xlam,flux,np(i))/(1.+z)
1	return
	end

	FUNCTION COLOR(I,J,X,Y,N,Z)

c	Returns color for filter pair (I,J) for s.e.d. in (X,Y) with N
c	data points observed at redshift Z. The zeropoint is not added
c	and must be added in the calling program.

	INCLUDE 'filter.dec'
	dimension a(2),iz(2),x(n),y(n)
	iz(1)=i
	iz(2)=j
	do k=1,2
	a(k)=filter(iz(k),x,y,n,z)
	if (a(k).le.0.) goto 1
	enddo
	color=-2.5*alog10(a(1)/a(2))
	return
c	used to be 1.e11
1	color=111.	
	return
	end

	FUNCTION ZEROP (I,J)

c	Returns zeropoint for filter pair (I,J). The A0 V stellar s.e.d.
c	is read from formatted file whose name is STARSED the first time
c	the function is used.

	INCLUDE 'filter.dec'
	character sedfile*80
	real xa0v(4000),ya0v(4000)
	save xa0v,ya0v
	if (jread.eq.0) then
		write (6,'(x,a)') 'Reading reference sed:'
		close (81)

c SUN Unix f77:	Get file name from environment variable A0VSED
		call getenv('A0VSED',sedfile)
		open (81,file=sedfile,form='formatted',status='old')

c VAX VMS Fortran: Read file assigned to A0VSED
c		open (81,name='A0VSED',form='formatted',status='old')

		read (81,'(a)',err=3) sedfile
		write (6,'(x,a)') sedfile (1:78)
		do n=1,10000
		read (81,*,end=1,err=3) xa0v(n),ya0v(n)
		enddo
1		close (81)
		jread=n-1
		write (6,'(i5,a,$)') jread,' data points'
		write (6,'(x,a)') '    ...done'
	endif
	zerop=-COLOR(i,j,xa0v,ya0v,jread,0.)
	return
3	stop 'Program exits because of error reading A0 V s.e.d. file'
	end

	SUBROUTINE FILTER0

c	Reads filter response functions from file FILTERBIN.RES

	INCLUDE 'filter.dec'
	character filtfile*80
	close (81)

c SUN Unix f77:	Get file name from environment variable A0VSED
		call getenv('FILTERS',filtfile)
		open (81,file=filtfile,form='unformatted',status='old')

c VAX VMS Fortran: Read file assigned to FILTERS
c		open (81,name='FILTERS',form='unformatted',status='old')

	l=largo(filtfile)
	write (6,'(x,2a)') 'Reading Filter File: ',filtfile(1:l)
	read (81,err=1) nf,np,r
	close (81)
	iread=1
	write (6,'(i3,a,$)') nf,' filter functions'
	write (6,'(x,a)') '    ...done'
	return
1	stop 'Program exits because of error reading file FILTERBIN.RES'
	end

	FUNCTION IFILTER()
c	Checks which filter file is in use.
	character filtfile*80
	call getenv('FILTERS',filtfile)
	ifilter=index(filtfile,'FILTERBIN.RES')
	return
	end

	BLOCK DATA FILTER_0
c	Parameter initialization for function FILTER
c	Array and common declarations for FUNCTION FILTER
c	mxft = 100 = maximum number of filters
c	mxwf = 250 = maximum number of wavelengths/filter
	parameter (mxft=100,mxwf=250)
	common /c_filter/ iread,jread,nf,np(mxft),r(mxwf,mxft,2)
	data iread/0/,jread/0/
	end

	FUNCTION TRAPEZ(Y,N,DX)
c	FINDS AREA BELOW CURVE (X,Y) ACCORDING TO TRAPEZOIDAL RULE.
c	ASSUMES EQUAL SPACING DX BETWEEN N POINTS.
	REAL Y(N)
	TRAPEZ=0.
	IF (N.LE.1) RETURN
	TRAPEZ=(Y(1) + Y(N))*DX/2.
	IF (N.EQ.2) RETURN
	A=0.	
	DO I=2,N-1
	A = A + Y(I)
	ENDDO
	TRAPEZ = TRAPEZ + A*DX
	RETURN
	END

	SUBROUTINE COPYRIGHT(LUN)
	data icount/0/
	write (lun,*)
	write (lun,'(x,a)') 'Isochrone Synthesis Algorithm'
	write (lun,'(x,a)') 'SUN/UNIX Version'
	write (lun,'(x,a)') '(C) 1995 - G. Bruzual and S. Charlot - All Rights Reserved'
	write (lun,*)
	icount=icount+1
	write (lun,'(x,a,i3)') 'Computing IS model No.',icount
	write (lun,*)
	return
	end

	FUNCTION LARGO(A)

c	Returns significant length of string a

	character*(*) a
	largo=0
	do i=1,len(a)
	if (a(i:i).ne.' ') largo=i
	enddo
	return
	end

	SUBROUTINE SFR_0_B(IDEF)

c	Selects parameters for SFR

	include 'SSP_13.dec'
	character ans*1

c	Ask for selection
	io=0
	tcut=20.E9
	if (idef.ne.0) then
		write (6,*)
		write (6,'(x,a)') 'Choose SFR: 0 = SSP (Delta Burst = zero length burst)'
		write (6,'(x,a)') '            1 = Exponential (enter Tau)'
		write (6,'(x,a)') '           -1 = Exponential (enter GALAXEV mu parameter)'
		write (6,'(x,a)') '            2 = Single Burst of finite length'
		write (6,'(x,a)') '            3 = Constant'
		write (6,'(x,a)') '            4 = Delayed'
		write (6,'(x,a)') '            5 = Linearly decreasing'
		write (6,'(x,a)') '            6 = Read SFR(t) from ASCII file'
10		write (6,'(x,a,$)') '   Choice = '
		read (5,'(i10)',err=10,end=6) io
		if (io.eq.6) io=7
		if (io.eq.5) io=8
		if (io.eq.4) io=6
	endif
	if (io.eq.1) then
c		Exponential SFR (enter tau)
1		write (6,'(x,a,$)') 'Exponential with e-folding time TAU (Gyr) = '
		read (5,'(f10.0)',err=1,end=6) tau
		tmu=1.-exp(-1./tau)
		write (6,'(x,a,f10.4,5x,a,f10.4)') 'mu =',tmu,'tau =',tau
		tau=1.e9*tau
		write (6,'(x,a,$)') 'Recycle gas ejected by stars Y/[N] = '
		read (5,'(a)',end=6) ans
		if (ans.eq.'Y'.or.ans.eq.'y') then
			call get_epsilon(io)
		else
			io=4
		endif
	elseif (io.eq.-1) then
c		Exponential SFR (enter mu)
2		write (6,'(x,a,$)') 'Exponential with GALAXEV mu parameter = '
		read (5,'(f10.0)',err=2,end=6) tmu
		tau=-1.e9/alog(1.-tmu)
		write (6,'(x,a,f10.4,5x,a,f10.4)') 'mu =',tmu,'tau =',tau*1.E-9
		write (6,'(x,a,$)') 'Recycle gas ejected by stars Y/[N] = '
		read (5,'(a)',end=6) ans
		if (ans.eq.'Y'.or.ans.eq.'y') then
			io=1
			call get_epsilon(io)
		else
			io=4
		endif
	elseif (io.eq.2) then
c		Long Burst SFR (enter duration of burst)
3		write (6,'(x,a,$)') 'Duration of burst (Gyr) = '
		read (5,'(f10.0)',err=3,end=6) tau
		tau=1.e9*tau
		tcut=tau
	elseif (io.eq.3) then
c		Constant SFR (enter constant value)
		tau=1.
5		write (6,'(x,a,$)') 'Enter SFR in Mo/yr [1] = '
		read (5,'(f10.0)',err=5,end=6) str
		if (str.gt.0.) tau=str
	elseif (io.eq.6) then
c		Delayed SFR (enter time at which maximum SFR occurs)
 		write (6,'(x,a  )') 'Delayed SFR as defined in Bruzual (1983)'
7		write (6,'(x,a,$)') 'Maximum in SFR at time TAU (Gyr) = '
		read (5,'(f10.0)',err=7,end=6) tau
		tau=1.e9*tau
	elseif (io.eq.7) then
c		Function SFR(t) read 2 column from ASCII file
 		write (6,'(x,a)') 't(yr), SFR(t) in Mo/yr read from disk file.'
 		write (6,'(x,a)') 'Linear interpolation between listed points.'
 		write (6,'(x,a)') 'First entry must correspond to t = 0.'
8 		write (6,'(x,a,$)') 'File name = '
		tau=usrsfr()
		if (tau.lt.0) goto 8
	elseif (io.eq.8) then
c		Linear SFR (enter time at which SFR  = 0)
 		write (6,'(x,a  )') 'Linearly decreasing SFR'
9		write (6,'(x,a,$)') 'SFR = 0 at time TAU (Gyr) = '
		read (5,'(f10.0)',err=9,end=6) tau
		tau=1.e9*tau
	endif
	last=0
	if (io.eq.0.or.io.eq.2) return
13	write(6,'(x,a,f4.1,a,$)')'Make SFR = 0 at time > TCUT [',tcut*1.e-9,' Gyr] = '
	read (5,'(f10.0)',err=13,end=6) ttcut
	if (ttcut.gt.0.) then
		tcut=1.e9*ttcut
		if (io.eq.1.or.io.eq.4) then
			agas=exp(-tcut/tau)
		else
			agas=rgas(tcut)
		endif
		write (6,'(x,a,f6.4,a)') 'Unprocessed gas at TCUT = ',agas,' Mo'
	endif
	return
6	stop
	end

	Function rgas(tcut)

c	Computes amount of unprocessed gas remaining at t=tcut, not including
c	gas ejected by dying stars.

	real tfe(500)
	dt=0.05E9
	tt=-dt
	do i=1,500
	tt=tt+dt
	if (tt.ge.tcut) goto 1
	tfe(i)=sfr(tt)
	enddo
1	rgas=1.-trapez(tfe,i-1,dt)
	if (rgas.lt.0.) rgas=0.
	return
	end

	SUBROUTINE GET_EPSILON(IO)

c	Gets fraction of ejected gas to be recycled in stars = epsilon

	include 'recycle.dec'

	write (6,'(1x,a)') 'Enter fraction of ejected gas to be recycled in stars = epsilon '
	write (6,'(1x,a)') 'Values from 0.001 to 1 have been experimented'
	write (6,'(1x,a)') 'Epsilon = 0.001 reproduces old_galaxev mu=0.50 model'
1	write (6,'(1x,a,$)') 'epsilon = '
	read (5,'(f10.0)',err=1,end=2) epsilon
	if (epsilon.le.0.) io=4
	if (epsilon.gt.1.) epsilon=1
	return
2	stop
	end

	SUBROUTINE EXPAND_TIME_STEPS(NSTEPS)

c	Expands time scale as required for model with tcut < 20 Gyr

	include 'csp.dec'
	include 'SSP_13.dec'
	real t(0:1000)

c	Build enlarged time scale
	k=-1
	do i=0,nsteps-1
	if (tb(i).le.tcut) then
		k=k+1
		last=i
		t(k)=tb(i)
		tlast=t(k)
		next=i+1
		tnext=tb(i+1)
	endif
	enddo
	m1=last

c	Add desired steps
	dt=0.002E9
	dt=dt/4.
	do i=1,100000
	tlast=tlast+dt
	if (tlast.lt.tnext) then
		k=k+1
		t(k)=tlast
	endif
	if (i.eq.20) dt=dt*4.
	enddo
	k1=k+1

c	Add remaining steps
	do i=next,nsteps-1
	k=k+1
	t(k)=tb(i)
	enddo

c	Shift sed's and other quantities for i>=next
	ks=nsteps-next
	do n=1,ks
	knew=k-n+1
	kold=nsteps-n
	do i=1,inw
	fl(i,knew)=fl(i,kold)
	enddo
	bflx(knew)=bflx(kold)
	strm(knew)=strm(kold)
	evfl(knew)=evfl(kold)
	snbr(knew)=snbr(kold)
	pnbr(knew)=pnbr(kold)
	bhtn(knew)=bhtn(kold)
	sntn(knew)=sntn(kold)
	wdtn(knew)=wdtn(kold)
	rmtm(knew)=rmtm(kold)
	enddo
	m2=knew

c	Interpolate SSP sed's and other quantities at new time steps
	do n=m1+1,m2-1
	a=(t(m2)-t(n))/(t(m2)-t(m1))
	b=1.-a
	do i=1,inw
	fl(i,n)=a*fl(i,m1)+b*fl(i,m2)
	enddo
	bflx(n)=a*bflx(m1)+b*bflx(m2)
	strm(n)=a*strm(m1)+b*strm(m2)
	evfl(n)=a*evfl(m1)+b*evfl(m2)
	snbr(n)=a*snbr(m1)+b*snbr(m2)
	pnbr(n)=a*pnbr(m1)+b*pnbr(m2)
	bhtn(n)=a*bhtn(m1)+b*bhtn(m2)
	sntn(n)=a*sntn(m1)+b*sntn(m2)
	wdtn(n)=a*wdtn(m1)+b*wdtn(m2)
	rmtm(n)=a*rmtm(m1)+b*rmtm(m2)
	enddo

c	Redefine time scale
	nsteps=k+1
	do i=0,nsteps-1
	tb(i)=t(i)
	enddo

	return
	end

	SUBROUTINE NAME_SED(LUN,JUN,KDIST,IGW,EVOFILE)

c	Selects options and builds output file names

	character evofile*80,phase(9)*6,fract(12)*4,stage(12)*4
	data phase/'ms','sgb','rgb','hb','agb','dcspn','cspn','wd','ccb'/
	data fract/'%14','%17','%22','%27','%U','%B','%V','%R','%I','%J','%K','%BOL'/
	data stage/'n14','n17','n22','n27','nU','nB','nV','nR','nI','nJ','nK','nBOL'/

c       Ask for file name (if not entered in command line)
        if (lun.lt.0) then
          write (6,'(/1x,a,$)') 'Generic file name for model (no extension) = '
          read (5,'(a)',end=1) evofile
          if (largo(evofile).eq.0) then
		evofile='junk'
          	write (6,'(/1x,2a )') 'Generic file name for model = ',evofile(1:largo(evofile))
	  endif
        else
          	write (6,'(/1x,2a )') 'Generic file name for model = ',evofile(1:largo(evofile))
        endif
	nun=lun
	lun=100
	jun=lun+50

c	File to write fluxes to compute G. Worthey's spectral indices
	if (igw.ne.0) then
		call chaext(evofile,'indx',nm)
		close (lun+10)
		open (lun+10,file=evofile,form='unformatted',status='unknown')
c		File to write spectral indices (1-11)
        	call chaext(evofile,'7index',nm)
        	close (lun+7)
        	open (lun+7,file=evofile,status='unknown')
        	call file_header(lun+7,evofile,0)
        	write (lun+7,206)
206     	format ('log age yr  1CN1   2CN2   3 Ca   4G4300 5 Fe   6 Fe',
     *		'   7 Fe   8 Fe  9Hbeta Fe5015 11 Mg1')
 
c		File to write spectral indices (12-21)
        	call chaext(evofile,'8index',nm)
        	close (lun+8)
        	open (lun+8,file=evofile,status='unknown')
        	call file_header(lun+8,evofile,0)
        	write (lun+8,207)
207     	format ('log age yr  12Mg2  13Mgb Fe5270 Fe5335  16Fe   17Fe',
     *		'   18Fe   19NaD  20TiO1 21TiO2')
		if (nun.eq.-3) return
	endif

c	File to write sed
	call chaext(evofile,'ised',nm)
	close (lun)
	open (lun,file=evofile,form='unformatted',status='unknown')

c	Files to write colors
	call chaext(evofile,'1color',nm)
	close (lun+1)
	open (lun+1,file=evofile,status='unknown')
        call file_header(lun+1,evofile,0)
	write (lun+1,101)
101	format (
     *	'log age yr   Mbol/Mo   Umag/Mo   Bmag/Mo   Vmag/Mo',
     *	'   Kmag/Mo     14-V      17-V      22-V      27-V',
     *	'     B(912)   B(4000)')
	call chaext(evofile,'2color',nm)
	close (lun+2)
	open (lun+2,file=evofile,status='unknown')
        call file_header(lun+2,evofile,0)
	write (lun+2,102)
102	format (
     *	'log age yr     U-J       J-F       F-N       U-B',
     *	'       B-V       V-R       V-I       V-J       V-K',
     *	'       R-I       J-H       H-K')
	call chaext(evofile,'3color',nm)
	close (lun+3)
	open (lun+3,file=evofile,status='unknown')
        call file_header(lun+3,evofile,0)
	write (lun+3,103)
103	format (
     *	'log age yr   Mbol/Mo   Vmag/Mo      M/Lb          M/Lv  ',
     *	'         M*           Mgas         SFR/yr       NLy/Mo   EW(Lya)      Mg2')
	call chaext(evofile,'4color',nm)
	close (lun+4)
	open (lun+4,file=evofile,status='unknown')
        call file_header(lun+4,evofile,0)
	write (lun+4,104)
104     format (
     &  'log age yr   Mbol/Mo   b(t)*''s/yr    B(t)/yr/Lo     SNR/yr/Lo'
     &  '    PNBR/yr/Lo       N(BH)         N(NS)         N(WD)'
     &  '      M(Remnants)')

	call chaext(evofile,'5color',nm)
	close (lun+5)
        open (lun+5,file=evofile,status='unknown')
        call file_header(lun+5,evofile,0)
        write (lun+5,108)
108     format ('log age yr   <H>    Hgam   Hdel   Hbet      B-K      B-K''')

c	Files to write partial seds's
	if (kdist.eq.0) return
	if (kdist.eq.1.or.kdist.eq.3) then
		do i=1,9
		call chaext(evofile,phase(i),nm)
		close (jun+i)
		open (jun+i,file=evofile,form='unformatted',status='unknown')
		enddo
	endif
	if (kdist.ge.2) then
		do i=1,12
		call chaext(evofile,fract(i),nm)
		close (lun+10+i)
		open (lun+10+i,file=evofile,status='unknown')
        	call file_header(lun+10+i,evofile,0)
		write (lun+10+i,105) fract(i)(2:4)
		enddo
		do i=1,12
		call chaext(evofile,stage(i),nm)
		close (lun+30+i)
		open (lun+30+i,file=evofile,status='unknown')
        	call file_header(lun+30+i,evofile,0)
		write (lun+30+i,106) stage(i)(2:4)
		enddo
	endif
105	format (
     *	'log age yr     %MS       %SGB      %RGB      %CHeB'
     *	'      %AGB    %CSPN      %WD      %CCN       %TRPH',
     *	'    TOTAL',x,a)
106	format (
     *	'log age yr    nMS   nSGB   nRGB   nCHeB   nAGB  nCSPN ',
     *	'   nWD   nCCB  nTRPH   NMS   NSGB   NRGB   NCHeB',
     *	'   NAGB  NCSPN    NWD   NCCB  NTRPH ',x,a)
	return
1	stop
	end

	SUBROUTINE CONVOLVE_SED(Y,K,BOL,STR,EVF,SNR,PNR,BH,SN,WD,RM)

c	Computes sed at age tb(k) by performing convolution of sed for a SSP
c	and the chosen SFR.

c	BOL = convolved bolometric flux at age tb(k)
c	STR = convolved total mass in stars at age tb(k)
c	EVF = convolved evolutionary flux at age tb(k)
c	SNR = convolved Super Nova rate at age tb(k)
c	PNR = convolved PN birth rate at age tb(k)
c	BH  = convolved total number of BH at age tb(k)
c	SN  = convolved total number of NS at age tb(k)
c	WD  = convolved total number of WD at age tb(k)
c	RM  = convolved total mass in Remnants at age tb(k)

c	Array declaration
	include 'SSP_13.dec'
	include 'csp.dec'
	real y(imw)

c	Choose routine
	if (tcut.lt.20.E9) then
		call convol2(y,k,bol,str,evf,snr,pnr,bh,sn,wd,rm)
	else
		call convol(y,k,bol,str,evf,snr,pnr,bh,sn,wd,rm)
	endif
	return
	end

	SUBROUTINE CONVOL(Y,IC,BOL,STR,EVF,SNR,PNR,BH,SN,WD,RM)

c	Convolution integral according to trapezoidal rule

	include 'SSP_13.dec'
	include 'csp.dec'
	real y(imw),w(0:jts)

c	Modified by G. Bruzual on 24/9/93 to include common /totgas/ where
c	the total mass in gas (new + recycled) vs time is stored. This
c	quantity is used in models with SFR which recycles gas.
	include 'recycle.dec'

c	Compute weights for each sed in convolution integral
	age=tb(ic)
	bol=0.
	str=0.
	evf=0.
	snr=0.
	pnr=0.
	bh=0.
	sn=0.
	wd=0.
	rm=0.
	do k=0,ic
	if (k.eq.0) then
		dt=tb(k+1)-tb(k)
	elseif (k.eq.ic) then
		dt=tb(ic)-tb(ic-1)
	else
		dt=tb(k+1)-tb(k-1)
	endif
	w(k)=sfr(age-tb(k))*dt/2.
	bol=bol+w(k)*bflx(k)
	str=str+w(k)*strm(k)
	evf=evf+w(k)*evfl(k)
	snr=snr+w(k)*snbr(k)
	pnr=pnr+w(k)*pnbr(k)
	bh =bh +w(k)*bhtn(k)
	sn =sn +w(k)*sntn(k)
	wd =wd +w(k)*wdtn(k)
	rm =rm +w(k)*rmtm(k)
	enddo
	str=amin1(1.,str)
c	Store amount of processed gas
	if (io.eq.1) then
c		unprocessed gas so far
		ugas=exp(-age/tau)
c		processed gas = gas formed into stars - mass in stars - remnants
		pgas = 1. - ugas - str - rm
		lgas=ic+1
		so(lgas)=pgas
		to(lgas)=age
	endif

c	Compute resulting sed
	do j=1,inw
	y(j)=0.
	do i=0,ic
	y(j)=y(j)+w(i)*fl(j,i)
	enddo
	enddo
	return
	end

	SUBROUTINE CONVOL2(Y,K,BOL,STR,EVF,SNR,PNR,BH,SN,WD,RM)

c	Works for finite length bursts and exponentially decaying SFR
c	truncated at t = tcut. These SFR's require special treatment
c	so that the time at which SFR becomes = 0 is seen at all ages.

c	Performs convolution required to derive flux of CSP from flux of SSP.
c	Compute integral from 0 to age of y(t')*sfr(t-t')dt', where age = x(k)

c	Modified by G. Bruzual on 20/6/94 to include common /totgas/ where
c	the total mass in gas (new + recycled) vs time is stored. This
c	quantity is used in models with SFR which recycles gas.
	include 'recycle.dec'

c	Array declarations
	include 'SSP_13.dec'
	include 'csp.dec'
	integer n(2000)
	real y(imw),w(0:jts),z(imw),t(2000)
	real*8 t8,tmin

c	At age = tb(k) find steps which contribute to convolution integral,
c	i.e. those for which tb(i) > tb(k)-tcut
	age=tb(k)
	tmin=dble(age)-dble(tcut)
	tmin=dmax1(0.D00,tmin)
	l=0
	do i=0,k
	t8=dble(tb(i))
	if (t8.eq.tmin) then
		l=l+1
		t(l)=tb(i)
		n(l)=i
	elseif (t8.gt.tmin) then
		if (l.eq.0) then
			l=l+1
			t(l)=tmin
			n(l)=-i
			a=dlog10(t8/tmin)/alog10(tb(i)/tb(i-1))
			do j=1,inw
			z(j)=a*fl(j,i-1)+(1.-a)*fl(j,i)
			enddo
			zm=a*strm(i-1)+(1.-a)*strm(i)
			zb=a*bflx(i-1)+(1.-a)*bflx(i)
			zf=a*evfl(i-1)+(1.-a)*evfl(i)
			zs=a*snbr(i-1)+(1.-a)*snbr(i)
			zp=a*pnbr(i-1)+(1.-a)*pnbr(i)
			zh=a*bhtn(i-1)+(1.-a)*bhtn(i)
			zn=a*sntn(i-1)+(1.-a)*sntn(i)
			zw=a*wdtn(i-1)+(1.-a)*wdtn(i)
			zr=a*rmtm(i-1)+(1.-a)*rmtm(i)
		endif
		l=l+1
		t(l)=tb(i)
		n(l)=i
	endif
	enddo

c	Compute weights for each sed in convolution integral
	do i=1,l
	if (i.eq.1) then
		dt=t(i+1)-t(i)
	elseif (i.eq.l) then
		dt=t(l)-t(l-1)
	else
		dt=t(i+1)-t(i-1)
	endif
	if (io.eq.2) then
		w(i)=dt/tau/2.
	else
		w(i)=sfr(age-t(i))*dt/2.
	endif
	enddo

c	Compute resulting sed
	do j=1,inw
	y(j)=0.
	do i=1,l
	if (n(i).lt.0) then
		y(j)=y(j)+w(i)*z(j)
	else
		y(j)=y(j)+w(i)*fl(j,n(i))
	endif
	enddo
	enddo

c	Compute BOL and STR, EVF, SNR, PNR, BH, NS, WD, RM
	bol=0.
	str=0.
	evf=0.
	snr=0.
	pnr=0.
	bh=0.
	sn=0.
	wd=0.
	rm=0.
	do i=1,l
	if (n(i).lt.0) then
		bol=bol+w(i)*zb
		str=str+w(i)*zm
		evf=evf+w(i)*zf
		snr=snr+w(i)*zs
		pnr=pnr+w(i)*zp
		 bh= bh+w(i)*zh
		 sn= sn+w(i)*zn
		 wd= wd+w(i)*zw
		 rm= rm+w(i)*zr
	else
		bol=bol+w(i)*bflx(n(i))
		str=str+w(i)*strm(n(i))
		evf=evf+w(i)*evfl(n(i))
		snr=snr+w(i)*snbr(n(i))
		pnr=pnr+w(i)*pnbr(n(i))
		 bh= bh+w(i)*bhtn(n(i))
		 sn= sn+w(i)*sntn(n(i))
		 wd= wd+w(i)*wdtn(n(i))
		 rm= rm+w(i)*rmtm(n(i))
	endif
	enddo
	str=amin1(1.,str)
c	Store amount of processed gas
	if (io.eq.1) then
c		unprocessed gas so far
		ugas=exp(-age/tau)
		if (age.gt.tcut) ugas=exp(-tcut/tau)
c		processed gas = gas formed into stars - mass in stars - remnants
		pgas = 1. - ugas - str - rm
		lgas=k+1
		so(lgas)=pgas
		to(lgas)=age
	endif
	return
	end

	FUNCTION SFR(TP)

c	Returns SFR at time TP

	include 'SSP_13.dec'

	sfr=0.
	if (tp.gt.tcut) return
	if (tp.lt.0.) then
		write (6,'(x,a,1pe12.4)') 'SFR called with tp < 0',tp
		return
	endif

c	Check for tcut

	if (io.eq.0) then
		if (tp.eq.0.) sfr=1.
	elseif (io.eq.1) then
		sfr=sfr_exp_rec(tp)
	elseif (io.eq.2) then
		if (tp.le.tau) sfr=1./tau
	elseif (io.eq.3) then
		sfr=tau
	elseif (io.eq.4) then
		sfr=exp(-tp/tau)/tau
	elseif (io.eq.6) then
		sfr=tp*exp(-tp/tau)/tau**2
	elseif (io.eq.7) then
		sfr=usrsfr(tp)
	elseif (io.eq.8) then
		sfr=2./tau*(1.-tp/tau)
		if (sfr.lt.0.) sfr=0.
	endif
	return
	end

	SUBROUTINE
     &	RF_COLOR(t,x,y,inw,lun,bolflux,strmass,sf,evflux,snbr,pnbr,bh,sn,wd,rm)

c	Array declarations
	parameter (nc=18,nb=18)
	character genfile*80,envfile*64
	integer no(nb),n1(nc),n2(nc),ly(6)
	real x(inw),y(inw),zp(nc),col(nc),fx(nb),balm(3)
	data icall/0/,ly/6*0/

	if (t.eq.0..or.bolflux.le.0.) return
	if (icall.eq.0) then
		icall=1

c		Modified 11/10/94:
c		To avoid recompiling this routine the arrays no,n1,n2 of
c		18 elements each are now read from a file.
c		Get file name from environment variable RF_COLORS_ARRAYS
        	envfile='RF_COLORS_ARRAYS'
        	call getenv(envfile,genfile)
        	close (1)
        	open (1,file=genfile,status='old',form='formatted',err=2)
		read (1,'(a)') genfile
		write (6,*) 'List of filters in file:'
		write (6,'(x,a)') genfile(1:largo(genfile))
c		Skip 18 lines of header
		do i=1,18
		read (1,*)
		enddo
        	read (1,'(18i5)') no
        	read (1,'(18i5)') n1
        	read (1,'(18i5)') n2
		close (1)
		write (6,*) 'Selected filters:'
		write (6,'(18i3)') n1
		write (6,'(18i3)') n2

c		Log of solar luminosity
		sl=33.+alog10(3.826)

c		Read filter file and compute zero points
		do i=1,nc
		zp(i)=zerop(n1(i),n2(i))

c		Fill arrays with filter numbers
		do j=1,nb
		if (n1(i).eq.no(j)) n1(i)=j
		if (n2(i).eq.no(j)) n2(i)=j
		if (no(j).eq.14) mb=j
		if (no(j).eq.15) nv=j
		enddo
		enddo

c		Find in array x the position of points used to define the
c		continuum at Lyman alpha
		do i=1,inw
		if (x(i).eq.1120.) ly(1)=i
		if (x(i).eq.1140.) ly(2)=i
		if (x(i).eq.1160.) ly(3)=i
		if (x(i).eq.1280.) ly(4)=i
		if (x(i).eq.1300.) ly(5)=i
		if (x(i).eq.1320.) then
			ly(6)=i
			goto 1
		endif
		enddo
	endif

c	Compute flux through each of nb filters
1	do i=1,nb
	fx(i)=filter(no(i),x,y,inw,0.)
	enddo

c	Compute colors
	do i=1,nc
	col(i)=zp(i)-2.5*alog10(fx(n1(i))/fx(n2(i)))
	enddo

c	Compute bolometric magnitude
	bolmag=4.75-2.5*alog10(bolflux)

c	Compute V magnitude for a 1 Mo galaxy
c	It is -27.5 magnitudes brighter for a 1E11 Mo galaxy
	vmag=2.422-2.5*alog10(fx(nv))

c	Compute U, B, K
	bmag=vmag+col(9)
	umag=bmag+col(8)
	gamk=vmag-col(13)

c	Compute mass-to-visual-light ratio in solar units
c	Using a G2 V sed and the filters number 14 and 15
c	in the filter file, one derives:
c		fblue(sun) = 0.138Lo
c		fvis (sun) = 0.113Lo
c	This numbers apply only to the filters in this filter library.
c       Express blue and visual flux of model galaxy (also measured in
c	Lo) in units of the blue and visual flux of the sun:
        fblu=fx(mb)/0.138
        fvis=fx(nv)/0.113
c       Total mass in galaxy  = 1 Mo
c       Compute mass-to-visual-light ratio
        blr=1./fblu
        vlr=1./fvis

c	Number of Lyman Continuum photons = Cly (log)
c	Flux in Lyman alpha from recombination theory
c	E(Lalpha) = 4.78E-13 * 33.1 * Nuv
c	log E = log(Nuv) -10.8 = cly -10.8
c	Number of Lyman continuum photons
	phly=clyman(x,y,inw)
	if (phly.gt.0.) then
		cly=sl+alog10(phly)
		fa=cly-10.8
	else
		cly=0.
		fa=0.
	endif

c	Stellar continuum at Lyman alpha
	scly=(y(ly(1))+y(ly(2))+y(ly(3))+y(ly(4))+y(ly(5))+y(ly(6)))/6.
	if (scly.gt.0.) then
		fc=sl+alog10(scly)
	else
		fc=0.
	endif

c	Ly alpha equivalent width assuming that the continuum is the stellar
c	continuum
	if (fa.gt.0..and.fc.gt.0.) then
		ew=10.**(fa-fc)
		ew2=phly/scly/10.**(10.8)
	else
		ew=0.
		ew2=0.
	endif

c	Compute Mg2 index
	ymg2=ymag2(x,y,inw)

c	Compute 912 A break
	b9=b912(x,y,inw)

c	Compute 4000 A break
	b4=b4000(x,y,inw)

c	Compute equivalent width of Balmer lines (Hgamma, Hdelta, Hbeta)
	ewbl=ew_balmer(x,y,inw,balm)

c	Compute specific flux, snbr, pnbr
	evf=evflux/bolflux
	snr=snbr/bolflux
	pnr=pnbr/bolflux

c	Compute mass in stellar remnants
c	Assume: BH = 2 Mo, NS = 1.4 Mo, WD = 0.55 Mo
	rm = 2.*bh + 1.4*sn + 0.55*wd

c	SFR/year
c	sf=sfr(t)

c	Write results
	tl=alog10(t)
	gasmass=1.-strmass
c	write (99,999) tl,phly,cly,fa,scly,fc,ew,ew2,ew2-ew
999	format (f10.6,1p8e12.4)
	write (lun+1,101) tl,bolmag,umag,bmag,vmag,gamk,(col(i),i=1,4),b9,b4
	write (lun+2,102) tl,(col(i),i=5,16)
	write (lun+3,103) tl,bolmag,vmag,blr,vlr,strmass,gasmass,sf,cly,ew,ymg2
	write (lun+4,104) tl,bolmag,evflux,evf,snr,pnr,bh,sn,wd,rm
	write (lun+5,105) tl,ewbl,balm,col(17),col(18)
101	format (f10.6,11f10.4)
102	format (f10.6,12f10.4)
103	format (f10.6,2f10.4,1p5e14.6,0pf10.4,f10.2,f10.4)
104	format (f10.6,f10.4,1p8e14.6)
105	format (f10.6,4f7.2,2f10.4)
	return
2	write (6,*) 'Error opening file: ',genfile(1:largo(genfile))
	stop
	end

      REAL FUNCTION LINEAR (X0,X,Y,N,I0)
c     INTERPOLATES LINEARLY THE FUNCTION Y(X) AT X=X0.
      REAL X(N),Y(N)
      IF (I0) 21,20,20
   20 I=IPLACE(X0,X,MAX0(1,I0),N)
      GOTO 22
   21 I=-I0
   22 I0=I
      IF (I.EQ.0) GOTO 2
      IF (X0.EQ.X(I).OR.X(I).EQ.X(I+1)) GOTO 1
      LINEAR=Y(I) + (Y(I+1)-Y(I))*(X0-X(I))/(X(I+1)-X(I))
      RETURN
    1 LINEAR=Y(I)
      RETURN
    2 write (6,3) X0
    3 FORMAT (' --- LINEAR:  X0 = ',1PE10.3,' is outside X range ---')
      LINEAR=0.
      RETURN
      END

	FUNCTION TRAPZ1 (X,Y,N)
	REAL X(N),Y(N)
	TRAPZ1=0.
	IF (N.EQ.1) GOTO 2
	DO 1 J=2,N
1	TRAPZ1= TRAPZ1 + ABS(X(J)-X(J-1))*(Y(J)+Y(J-1))/2.
	RETURN
2	TRAPZ1=Y(1)*X(1)/2.
	RETURN
	END

        FUNCTION USRSFR(TP)

c	Returns SFR computed according to usr defined SFR(t) read from file.

c	Array declarations
        parameter (nsfrp=1000)
        character namex*64
        real time(nsfrp),usr_sfr(nsfrp)
	data isfrc/0/

c	Read file if first time that function is called
	if (isfrc.eq.0) then
                read (5,'(a)',end=10) namex
                close (1)
                open (1,file=namex,status='old',err=10)
                do i=1,nsfrp
                read (1,*,end=1) time(i),usr_sfr(i)
                enddo
1               isfrc=i-1
		write (6,*) isfrc,' data points read from file'
                close (1)
        endif

c	Interpolate SFR at time TP
        if (tp.lt.0.) then
                usrsfr=0.
        elseif (tp.eq.0.) then
                usrsfr=usr_sfr(1)
        elseif (tp.gt.time(isfrc)) then
                usrsfr=0.
        else
                call locate (time,isfrc,tp,i1)
                a1=(tp-time(i1))/(time(i1+1)-time(i1))
                usrsfr=a1*usr_sfr(i1+1)+(1.-a1)*usr_sfr(i1)
        endif
        return
10	write (6,'(1x,a)') 'File not found'
	usrsfr=-100.
	return
	end

	SUBROUTINE CHAEXT(S,E,N)

c	Changes extension (suffix) to filename s
c	SUN/FORTRAN version. G. Bruzual. 08-NOV-1988

	character*(*) s,e

	l=len(s)
	k=len(e)
	id=index(s,'.')
	ib=index(s,' ')	
	if (id.eq.0) id=ib
	s(id:id)='.'
	if (id+k.gt.l) k=l-id
	do i=1,k
	s(id+i:id+i)=e(i:i)
	enddo
	n=id+k
	do i=id+k+1,l
	s(i:i)=' '
	enddo
	return
	end

	SUBROUTINE FILE_HEADER(IUN,NAME,LISTED)

c	Writes header information in file iun

	include 'SSP_4.dec'
	include 'SSP_13.dec'
	include 'cosmo.dec'
	character name*(*),und,buffer*32,blank*32
	data und/'-'/,blank/'                                '/

c	Date file
	call dattim(iun,0,'L')

c	Clear file name
	ldot=index(name,'.')-1
	buffer(1:ldot)=name(1:ldot)
	buffer(ldot+1:32)=blank(ldot+1:32)

c	Write top lines of header
	write (iun,200) (und,i=1,120)
200	format (11x,'I',120a,'I')
	write (iun,201)
201	format (11x,'I',120x,'I')
	write (iun,202) buffer
202	format (11x,'I      IS_GALAXEV  ---  MODEL PARAMETERS:   Generic file name for this model = ',a,10X,'I')
	write (iun,201)
	write (iun,203) id
203	format (11x,'I      TRACKS: ',a,26X,'I')
	write (iun,201)

c	Write information about SFR:
	if (io.eq.0) then
		write (iun,204)
204		format (11x,'I      S.F.R.: SSP = Zero Length Burst at t = 0',74X,'I')
		write (iun,201)
	elseif (io.eq.1) then
		t9=tau*1.e-9
		tmu=1.-exp(-1./t9)
		write (iun,205) tmu,t9
205		format (11x,'I      S.F.R.: Exponential with MU9 = ',F5.3,'/Gyr',6X,'TAU = ',F7.3,' Gyr',
     *		' (includes processed gas recycling)',16X,'I')
		write (iun,201)
	elseif (io.eq.2) then
		write (iun,206) tau
206		format (11x,'I      S.F.R.: Finite Burst of Duration = ',1pe9.3,' yr',67X,'I')
		write (iun,201)
	elseif (io.eq.3) then
		write (iun,207) tau
207		format (11x,'I      S.F.R.: Constant = ',1pe10.3,' Mo/yr',79X,'I')
		write (iun,201)
	elseif (io.eq.4) then
		t9=tau*1.e-9
		tmu=1.-exp(-1./t9)
		write (iun,208) tmu,t9
208		format (11x,'I      S.F.R.: Exponential with MU9 = ',F5.3,'/Gyr',6X,'TAU = ',F7.3,' Gyr',
     *		' (does not include processed gas recycling)', 8X,'I')
		write (iun,201)
	elseif (io.eq.5) then
		ldot=index(name1,' ')-1
		buffer(1:ldot)=name1(1:ldot)
		buffer(ldot+1:32)=blank(ldot+1:32)
		write (iun,209) t0(1)*1.E-9,s(1),buffer
209		format (11x,'I      S.F.R.: 2 Bursts: Burst 1 at ',F6.3,'/Gyr, Strength = ',F6.4,', in file = ',a,12x,'I')
		ldot=index(name2,' ')-1
		buffer(1:ldot)=name2(1:ldot)
		buffer(ldot+1:32)=blank(ldot+1:32)
		write (iun,210) t0(2)*1.E-9,s(2),buffer
210		format (11x,'I                        Burst 2 at ',F6.3,'/Gyr, Strength = ',F6.4,', in file = ',a,12x,'I')
	else
		write (iun,201)
		write (iun,201)
	endif
	write (iun,201)

c	Write information about IMF
	write (iun,211) iseg
211	format (11x,'I      I.M.F.: Power law (',I2,' segments):',82X,'I')
	write (iun,212)
212	format (11x,'I                                                                         mass      number',31x,'I')
	write (iun,213)
213	format (11x,'I                                              x   from m     to m    fraction    of stars      c',24x,'I')
        do i=1,iseg
        write (iun,214) xx(i),lm(i),um(i),baux(i),cn(i),cc(i)
214     format (11x,'I',40x,f7.2,f9.2,f9.2,2f12.4,1pe12.4,19x,'I')
        enddo
	write (iun,201)
        write (iun,215) totm,totn,avs
215     format (11x,'I',59x,'totals',2f12.4,f8.4,' Mo/star',15x,'I')
	do i=1,6-iseg
	write (iun,201)
	enddo
	if (listed.eq.0) then
		write (iun,216)
216		format (11x,'I      LISTED: Rest frame properties',85X,'I')
		write (iun,201)
	else
		ttg=tg*1.E-9
		tu=t(h,q,0.)
		zf=zx(ttg,h,q)
		write (iun,217) h,q,ttg,tu,zf
217		format (11x,'I      LISTED: Observer frame properties for the following cosmology:',52x,'I'/,
     *		11x,'I',30x,'Ho = ',f4.0,3x,' qo = ',f7.4,3x,'tg = ',f5.2,' Gyr',3x,
     *		'tu = ',f5.2,' Gyr', 3x,' zf = ',f6.2,16x,'I')
	endif
	write (iun,201)
	write (iun,218)
218	format (11x,'I',32X,'(C) 1995 G. Bruzual A. & S. Charlot - All Rights Reserved',31x,'I')
	write (iun,200) (UND,I=1,120)
	write (iun,*)
	return
	end

	FUNCTION SFR_EXP_REC(TP)

c	Returns Exponential SFR including processed gas recycling
c	(after GALAXEV mu models).

	include 'SSP_12.dec'
	include 'SSP_13.dec'
	real to(300),so(300)

c	Init SFR storage arrays
	if (last.eq.0) then
c		Compute mass in stars according to SSP needed if io=1
		last=last+1
		to(1)=0.
		so(1)=alog10(1./tau)
	endif

c	Locate t in array to. Add new point to sfr array so if needed.
	if (tp.eq.0.) then
		sfr_exp_rec=10.**so(1)
		return
	elseif (tp.eq.to(last)) then
		sfr_exp_rec=10.**so(last)
		return
	elseif (tp.gt.to(last)) then
c		Compute total mass in stars at age to(last)
		last=last+1
		to(last)=tp
		ww=0.
		jc=last-2
		do k=0,jc
		if (k.eq.0) then
			dt=tb(k+1)-tb(k)
			sf=10.**so(last)
		elseif (k.eq.jc) then
			dt=tb(jc)-tb(jc-1)
			sf=10.**so(1)
		else
			dt=tb(k+1)-tb(k-1)
			call locate(to,last,tb(jc)-tb(k),i)
			if (i.gt.0.and.i.lt.last) then
				a=(tp-to(i))/(to(i+1)-to(i))
				sf=(1.-a)*so(i)+a*so(i+1)
				sf=10.**sf
			else
				sf=0.
				write (6,*) ' SFR (last): undefined age',tb(jc)-tb(k)
			endif
		endif
		ww=ww+sf*strm(k)*dt
		enddo
c		Compute total mass in gas at age to(last)
		ww=1.-ww/2./tau
c		Unprocessed gas at age to(last)
		unp=exp(-tp/tau)
c		Compute amount of recycled gas at age to(last)
		rec=ww-unp
c		SFR without recycling
		su=unp/tau
c		Contribution of recycled gas to SFR
		sr=rec*exp(-tp/tau)/tau
c		Total SFR
		sf=su+sr
		so(last)=alog10(sf)
	endif

	call locate(to,last,tp,i)
	if (i.gt.0.and.i.lt.last) then
		a=(tp-to(i))/(to(i+1)-to(i))
		sf=(1.-a)*so(i)+a*so(i+1)
		sfr_exp_rec=10.**sf
	else
		sfr_exp_rec=0.
		write (6,*) ' SFR: undefined age',tp
	endif
	return
	end

	FUNCTION CLYMAN(X,Y,N)

c	Compute number of Lyman continuum photons in sed Y(X).
c	Assumes X is in Angstroms and Y in ergs/sec/Angstroms (physical flux)

	real x(n),y(n),w(100),f(100)
	data icall/0/,const/0./,wly/912./

c	compute proportionality constant
	if (icall.eq.0) then
		c=2.997925E10
		h=6.6262E-27
		const=1.0E-8/h/c
		icall=1
	endif

c	find Lyman limit in sed and log(number of photons)
	do i=1,n
	if (x(i).lt.wly) then
		w(i)=x(i)
		f(i)=w(i)*y(i)
	elseif (x(i).eq.wly) then
		w(i)=x(i)
		f(i)=w(i)*y(i)
		goto 1
	elseif (x(i).gt.wly) then
		w(i)=wly
		f(i)=y(i-1)+(w(i)-x(i-1))*(y(i)-y(i-1))/(x(i)-x(i-1))
		f(i)=w(i)*f(i)
		goto 1
	endif
	enddo
1	clyman=const*trapz1(w,f,i)
	return
	end

	FUNCTION YMAG2(WL,F,NI)

c	Computes Mg2 Index defined by Burstein, Faber, et al.
c	Written by G. Magris (May 1991)

	real wl(ni),f(ni),w0(6),wc(3),fl(25),wi(75),fi(3),wn(25),delta(3)
	real linear
	data nw,w0/3,4897.,4958.25,5156.,5197.25,5303.,5366.75/

	ymag2=0.
	if (ni.ne.1206) return

	wc(1)=(w0(1)+w0(2))/2.
	wc(3)=(w0(5)+w0(6))/2.
	wc(2)=(w0(3)+w0(4))/2.
	delta(1)=w0(2)-w0(1)
	delta(3)=w0(6)-w0(5)
	delta(2)=w0(4)-w0(3)

	np=21
	do j=1,3
	k=2*j-1
	del=(w0(k+1)-w0(k))/np
		do i=1,np+1
		l=i+(np+1)*(j-1)
		wi(l)=w0(k)+del*(i-1)
		enddo
	enddo

	do j=1,3
		i0=0
		do i=1,np+1
		l=i+(np+1)*(j-1)
		wn(i)=wi(l)
		fl(i)= linear(wi(l),wl,f,ni,i0)
		enddo
	fi(j)=trapz1(wn,fl,np+1)/delta(j)
	enddo

	fc=fi(1)+(fi(3)-fi(1))/(wc(3)-wc(1))*(wc(2)-wc(1))
	ymag2=-2.5*alog10(fi(2)/fc)

	return
	end
	FUNCTION B912(X,Y,N)

c	Returns 912 A break amplitude for sed in (x,y).
c	The break is defined as the ratio of the average Fnu flux densities:
c	(800-900)/(1000-1100) (Bruzual (1983).

	real x(n),y(n),w(100),z(100)
	data icall/0/
	b912=0.
	if (n.ne.1206) return
	if (icall.eq.0) then
		x1=800.
		call locate(x,n,x1,i1)
		a1=(x1-x(i1))/(x(i1+1)-x(i1))
		x2=900.
		call locate(x,n,x2,i2)
		a2=(x2-x(i2))/(x(i2+1)-x(i2))
		x3=1000.
		call locate(x,n,x3,i3)
		a3=(x3-x(i3))/(x(i3+1)-x(i3))
		x4=1100.
		call locate(x,n,x4,i4)
		a4=(x4-x(i4))/(x(i4+1)-x(i4))
		icall=1
	endif

c	Compute fluxes and transform to Fnu units
	i=1
	w(i)=x1
	z(i)=a1*y(i1+1)+(1.-a1)*y(i1)
	z(i)=z(i)*w(i)**2
	do j=i1+1,i2
	i=i+1
	w(i)=x(j)
	z(i)=y(j)*x(j)**2
	enddo
	i=i+1
	w(i)=x2
	z(i)=a2*y(i2+1)+(1.-a2)*y(i2)
	z(i)=z(i)*w(i)**2
	fl=trapz1(w,z,i)/(w(i)-w(1))
	i=1
	w(i)=x3
	z(i)=a3*y(i3+1)+(1.-a3)*y(i3)
	z(i)=z(i)*w(i)**2
	do j=i3+1,i4
	i=i+1
	w(i)=x(j)
	z(i)=y(j)*x(j)**2
	enddo
	i=i+1
	w(i)=x4
	z(i)=a4*y(i4+1)+(1.-a4)*y(i4)
	z(i)=z(i)*w(i)**2
	fr=trapz1(w,z,i)/(w(i)-w(1))
	b912=fr/fl
	return
	end
	FUNCTION B4000(X,Y,N)

c	Returns 4000 A break amplitude for sed in (x,y)
c	The break is defined as the ratio of the average Fnu flux densities:
c	(4050-4250)/(3750-3950) (Bruzual (1983), Hamilton 1985 ApJ 297, 371).

	real x(n),y(n),w(100),z(100)
	data icall/0/
	b4000=0.
	if (n.ne.1206) return
	if (icall.eq.0) then
		icall=1
		do i=1,n

c		if (x(i).eq.3770.) i1=i
c		if (x(i).eq.3800.) i2=i
c		if (x(i).eq.3890.) i3=i
c		if (x(i).eq.3920.) i4=i

		if (x(i).le.3761.) i1=i
		if (x(i).eq.3810.) i2=i
		if (x(i).eq.3850.) i3=i
		if (x(i).eq.3920.) i4=i

		if (x(i).eq.4050.) j1=i
		if (x(i).eq.4250.) then
			j2=i
			goto 1
		endif
		enddo
	endif

c	Transform to Fnu units
1	i=0
	do j=j1,j2
	i=i+1
	w(i)=x(j)
	z(i)=y(j)*x(j)**2
	enddo
	fr=trapz1(w,z,i)/(x(j2)-x(j1))

	i=0
	do j=i1,i2
	i=i+1
	w(i)=x(j)
	z(i)=y(j)*x(j)**2
	enddo
	fl1=trapz1(w,z,i)/(x(i2)-x(i1))

	i=0
	do j=i3,i4
	i=i+1
	w(i)=x(j)
	z(i)=y(j)*x(j)**2
	enddo
	fl2=trapz1(w,z,i)/(x(i4)-x(i3))

	fl=(fl1+fl2)/2.

	b4000=fr/fl
	return
	end
	FUNCTION EW_BALMER(X,Y,N,H)

c	Computes equivalent width of the H_betha, H_gamma and H_delta lines
c	Computes the average of these 3 values

	real x(n),y(n),w(50),z(50),h(3)
	integer ip(3),im(3),io(3)
	data icall/0/,ip/4,3,4/,im/4,10,4/,io/3*0/

c	Find position of Balmer lines
	ew_balmer=0.
	if (n.ne.1206) return
	if (icall.eq.0) then
		icall=1
		do i=1,n
c		H_delta
		if (x(i).eq.4100.) io(1)=i
c		H_gamma
		if (x(i).eq.4340.) io(2)=i
c		H_betha
		if (x(i).eq.4860.) then
			io(3)=i
			goto 1
		endif
		enddo
	endif

c	Compute equivalent widths
1	ew_balmer=0.
	do k=1,3
	i1=io(k)-im(k)
	i2=io(k)+ip(k)
	i=0
	do j=i1,i2
	a=(x(i2)-x(j))/(x(i2)-x(i1))
	fc=a*y(i1)+(1.-a)*y(i2)
	i=i+1
	w(i)=x(j)
	z(i)=1.-y(j)/fc
	enddo
	if (k.eq.2) then
c		Supress G-band (make profile symmetrical)
		w(1)=w(7)
		z(1)=z(14)
		w(2)=w(8)
		z(2)=z(13)
		do i=3,8
		w(i)=w(i)+6
		z(i)=z(i+6)
		enddo
		i=8
	endif
	h(k)=trapz1(w,z,i)
	if (h(k).lt.0.) h(k)=0.
	ew_balmer=ew_balmer+h(k)
	enddo
	ew_balmer=ew_balmer/3.
	return
	end
      INTEGER FUNCTION IPLACE(X0,XX,N1,N2)
c     FINDS L SUCH THAT   XX(L).LT.X0.LT.XX(L+1)
      DIMENSION XX(N2)
      X(I)=XX(N1+I-1)
      N=N2-N1+1
      I=1
      IF (X(1).GT.X(2)) I=2
      L=0
    1 L=L+1
      IF (L.EQ.N) GOTO 4
      GOTO (2,3),I
    2 IF (X(L).LE.X0.AND.X0.LT.X(L+1)) GOTO 5
      GOTO 1
    3 IF (X(L).GE.X0.AND.X0.GT.X(L+1)) GOTO 5
      GOTO 1
    4 IF (X0.NE.X(N)) GOTO 6
    5 IPLACE=L+N1-1
      RETURN
    6 IPLACE=0
      RETURN
      END

      SUBROUTINE LOCATE(XX,N,X,J)
      DIMENSION XX(N)
      JL=0
      JU=N+1
10    IF(JU-JL.GT.1)THEN
        JM=(JU+JL)/2
        IF((XX(N).GT.XX(1)).EQV.(X.GT.XX(JM)))THEN
          JL=JM
        ELSE
          JU=JM
        ENDIF
      GO TO 10
      ENDIF
      J=JL
      RETURN
      END
	subroutine dattim(ifile,k,a)

c	Prints current time and date at center of page

	character a,date*24
	call fdate(date)
	if (a.eq.'s'.or.a.eq.'S') write(ifile,'(23x,a)') date
	if (a.eq.'l'.or.a.eq.'L') write(ifile,'(54x,a)') date
	return
	end
	FUNCTION T(H,Q,Z)

c	Returns age of universe at redshift z (revised 6/16/83, Durham)

c	H = Ho in km/sec/Mpc
c	Q = qo  (if problems with qo = 0, try 0.0001)

	a(q,z)=sqrt(1.+2.*q*z)/(1.-2.*q)/(1.+z)
	b(q)=q/(abs(2.*q-1.))**1.5
	c(q,z)=(1.-q*(1.-z))/q/(1.+z)

	acosh(x)=alog(x+sqrt(x**2-1.))
c	h0=h*0.001021	! in (billion years)**(-1)
	h0=h*0.001021

	if     (q.eq.0.0) then
		t=1./(1.+z)
	elseif (q.lt.0.5) then
		t=a(q,z) - b(q)*acosh(c(q,z))
	elseif (q.eq.0.5) then
		t=2./3./(1.+z)**1.5
	else
		t=a(q,z) + b(q)*acos(c(q,z))
	endif
	t=t/h0
	return
	end
      FUNCTION ZX(TX,H,Q)

c     Returns the value of Z = ZX (redshift) corresponding to a given
c     light travel time TX (measured in Gyr).

c	H = Ho in km/sec/Mpc
c	Q = qo (if problems with qo = 0, try 0.0001)
      REAL LTT,Z(46)
      DATA  Z/0.,.001,.002,.004,.006,.008,.01,.02,.04,.06,.08,.1,.2,.3,
     &.4,.5,.545,.6,.7,.8,.9,.945,1.,1.2,1.4,1.6,1.8,2.,3.,4.,5.,6.,
     &   7.,8.,9.,10.,12.,14.,16.,18.,20.,40.,60.,80.,100.,1000./
c     LTT(Q,Z)=AGE-T(H,Q,Z)
      ZX=0.
      IF (TX.EQ.0.) RETURN
      AGE=T(H,Q,0.)
      ZX=-2.
      IF (TX.GE.AGE) RETURN
c     H0=H*0.001021     ! IN BILLION YEARS ** (-1)
      H0=H*0.001021
      IF (Q.EQ.0.5) GOTO 4
      DO 1 J=1,46
      LTT=AGE-T(H,Q,Z(J))
    1 IF (TX.LE.LTT) GOTO 2
    2 ZX=Z(J-1)
      DO 3 J=1,1000
      DZ=H0*(TX-T(H,Q,0.)+T(H,Q,ZX))*(1.+ZX)**2*(1.+2.*Q*ZX)**0.5
      IF (ABS(DZ/ZX).LT.0.0001) RETURN
    3 ZX=ZX+DZ
    4 ZX=(1.-3.*H0*TX/2.)**(-2./3.)  - 1.
      RETURN
      END

