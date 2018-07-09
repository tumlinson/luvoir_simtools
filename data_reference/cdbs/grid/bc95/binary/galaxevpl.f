! ::::::::::::::
! galaxevpl.f
! ::::::::::::::
	PROGRAM GALAXEVPL

!	WRITES A FORMATTED FILE WITH GALAXY SPECTRAL ENERGY DISTRIBUTIONS
!	PRODUCED BY PROGRAM GALAXEV THAT CAN BE USED AS INPUT FOR PLOTING
!	WITH PROGRAM PL.EXE.

!	Compile in HP UNIX with:

!		f77 -O -K +es +U77 galaxevpl -o galaxevpl

	CHARACTER NAMECH*256,ext*12,name2*256,ans
	INTEGER N(12)
!	REAL X(24),C(12),T(200),CNU(4000),W(4000),F(4000,200)
	REAL X(24),C(12),T(400),CNU(2000),W(2000),F(2000,400)

	write (6,*)
	write (6,'(x,a)') 'GALAXEVPL:'
	write (6,'(x,2a)') 'This program will write a formatted file ',
     &  'with galaxy s.e.d.''s'
	write (6,'(x,2a)') 'written in an unformatted *.SED file by ',
     &  'program GALAXEV.'
1	write (6,*)
	write (6,'(x,a,$)') 'Input file name (CTRL/D exits) = '
	READ (5,'(a)',END=3) NAMECH
	CLOSE (1)
	OPEN (1,FILE=NAMECH,STATUS='OLD',FORM='UNFORMATTED',ERR=25)
	READ (1) KS,(T(I),I=1,KS)
	READ (1) IW,(W(I),I=1,IW)
!	ip = Number of flux values to be printed
	if (iw.eq.352) then
!		352 => YGALAXEV
		ip=iw-10
		io=1
	elseif (iw.eq.1166) then
!		1166 => GALAXEV + IRAS
		ip=iw
		io=1
	elseif (iw.eq.965) then
!		965 => Guiderdoni + Rocca-Volmerange models
		ip=iw
		io=1
	elseif (ks.gt.100) then
!		IS_GALAXEV model
		ip=iw
		io=0
	else
		IP=IW-17
		io=1
	endif
	write (6,100) KS
100	FORMAT (/' In this file there are',I4,' galaxy s.e.d.''s ',
     &  'corresponding to the'/' following record numbers and ages ',
     &  '(in Gyr):'/)
	DO I=KS+2,200
	T(I)=0.0
	ENDDO
	NL=KS/5
!	IF (NL*5.LT.KS) NL=NL+1   ! number of lines to type in screen
	IF (NL*5.LT.KS) NL=NL+1
	DO J=1,NL
	JF=4*NL+J
	if (mod(j,21).eq.0) then
		lper=(100*J)/nl
		if (lper.gt.99) lper=99
		write (6,'(a,i2,a,$)') '--More--(',lper,'%) '
		read (5,'(a)',end=4) ans
		if (ans.eq.'q'.or.ans.eq.'Q') goto 4
	endif
	write (6,101) (I,T(I+IO)*1.E-9,I=J,JF,NL)
101	FORMAT (5(I3,F9.5,' |'))
	ENDDO
4	write (6,102) W(1),W(IP),IP
102	FORMAT (/' Each sed covers from lambda = ',F5.0,
     &  ' to lambda = ',1pe12.5,
     &  ' A in ',I4,' steps.'/' Enter desired wavelength range',
     &  ' = [W1,W2] (default: full range).'/
     &  ' If you want all s.e.d.''s scaled to flux = F0 at lambda = W0,',
     &  ' enter the'/' desired values (default: no scaling)'/' If you',
     &  ' want the output as Fnu vs. lambda, enter W1 with a minus sign.')
15	write (6,'(/x,a,$)') 'W1,W2,W0,F0 = '
	call nread(x,4,*15,*3)
	w1=x(1)
	w2=x(2)
	w0=x(3)
	f0=x(4)
	I1=1
	I2=IP
	I0=0
	NU=0
	IF (W1.LT.0) NU=1
	W1=ABS(W1)
	DO I=1,IP
	CNU(I)=1.
	IF (NU.NE.0) CNU(I)=W(I)*W(I)*1.E-8/3.E10
	IF (W(I).LE.W0) I0=I
	IF (W(I).LE.W1) I1=I
	IF (W(I).LE.W2) I2=I
	ENDDO
	IF (I1.GE.I2) GOTO 1
	write (6,'(/x,a)') 'Enter up to 12 s.e.d. record numbers'
	write (6,'(x,a,$)') 'Record numbers (separated by commas) = '
	READ (5,'(12i5)',END=3) N
	IC=0
	DO 2 I=1,12
	IF (N(I).EQ.0) GOTO 2
	IC=IC+1
2	CONTINUE
	IF (IC.EQ.0) GOTO 1
	if (io.gt.0) then
		DO J=1,KS
		READ (1) (F(I,J),I=1,IP)
		ENDDO
	else
		DO J=1,KS
		READ (1) IP,(F(I,J),I=1,IP)
		ENDDO
	endif
	DO I=1,IC
	IF (F0.GT.0.) C(I)=F0/F(I0,N(I))/CNU(I0)
	IF (F0.EQ.0.) C(I)=1
	ENDDO
	if (n(1).lt.10) then
		write (ext,'(i1)') n(1)
	elseif (n(1).lt.100) then
		write (ext,'(i2)') n(1)
	elseif (n(1).lt.1000) then
		write (ext,'(i3)') n(1)
	else
		ext='glxvpl'
	endif
	call chaext(namech,ext,nm)
	l=largo(namech)
	write (6,*)
	write (6,'(x,3a,$)') 'Output file name [',namech(1:l),'] = '
	READ (5,'(a)',END=3) NAME2
	if (name2(1:2).ne.'  ') namech=name2
	CLOSE (2)
	OPEN (2,FILE=NAMECH,FORM='FORMATTED')
	write (2,108) (T(N(J)+IO),J=1,IC)
	write (6,108) (T(N(J)+IO),J=1,IC)
108	FORMAT ('Lambda(A)\\Age',1p12E11.3)
	DO I=I1,I2
	WRITE (2,109) W(I),(C(J)*CNU(I)*F(I,N(J)),J=1,IC)
109	FORMAT (1PE13.6,12E11.3)
	ENDDO
	GOTO 1
25	write (6,'(x,a)') 'File not found'
	goto 1
3	END
! ::::::::::::::
! nread.f
! ::::::::::::::
	SUBROUTINE NREAD(X,NA,*,*)

!	This routine is useful when reading several parameters separated by
!	commas (not supported by current version of f77 in Sun 4/110).

!	Returns NA arguments in array X (read from the screen).
!	RETURN 1: Statement to execute if error while reading.
!	RETURN 2: Statement to execute if EOF detected.

	parameter (npar=24)
	character b*132
	real x(npar)

!	Clear buffer
	do i=1,npar
	x(i)=0.
	enddo

!	Read string b
	read (5,'(a)',end=2) b

!	Number of characters read into b
	na=index(b,' ')-1
	if (na.eq.0) return

!	Adds "," at the end of string b to guarantee extraction of last value
	b(na+1:na+1)=','

!	Extract numbers from b
	n=0
	l1=0
	do i=1,100
	l1=l1+n+1
	n=index(b(l1:),',')-1
	if (n.eq.0) then
		x(i)=0.
	elseif (n.gt.0) then
      		read(b(l1:l1+n-1),'(G132.0)',err=1) x(i)
	else
		na=i-1
		return
	endif
	enddo
1	return 1
2	return 2

	ENTRY QREAD(V,K,*,*)

!	Emulates q format of VMS/Fortran

!	V = required value
!	K = number of characters typed
!	RETURN 1: Statement to execute if error while reading.
!	RETURN 2: Statement to execute if EOF detected.

!	Read string b and assign value to v
	read (5,'(a)',end=4) b
	k = index(b,' ') - 1
	v=0.
	if (k.gt.0) then
      		read(b(:k),'(G132.0)',err=3) v
	endif
	return
3	return 1
4	return 2
	end
! ::::::::::::::
! chaext.f
! ::::::::::::::
	SUBROUTINE CHAEXT(S,E,N)

!	Changes extension (suffix) to filename s
!	SUN/FORTRAN version. G. Bruzual. 08-NOV-1988

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

	FUNCTION LARGO(A)

!	Returns significant length of string a

	character*(*) a
	largo=0
	do i=1,len(a)
	if (a(i:i).ne.' ') largo=i
	enddo
	return
	end

