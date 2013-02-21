library(plotrix)
library(png)

#download up-to-date sea ice volume data from PIOMAS: http://psc.apl.washington.edu/wordpress/research/projects/arctic-sea-ice-volume-anomaly/
icevolume <- read.table("seaicevolume.dat.csv",head=T) 
icedeg <- icevolume$day/365*360
icevolume <- cbind(icevolume,icedeg)

img<-readPNG("arctic-ocean-trans2_800px.png")

monthlabel <- c("January","February","March","April","May","June","July","August","September","October","November","December")
monthdeg <- c(0,30,60,90,120,150,180,210,240,270,300,330)

png(filename = "pics3/ice5%03d.png", width = 800, height = 800, units = "px") 

for (i in 12108:(dim(icevolume)[1])) {
 if (i %% 3 != 0) {
  } else {	

  	year <- icevolume$year[i]
  	par(cex=2,cex.axis=1.2,cex.lab=1.2, cex.main=1.2)
  	polar.plot(0, 0, clockwise=T, start=-20, rp.type="s", point.symbols='.', point.col='blue', radial.lim=c(0,5,15,25,35),radial.labels=c(NA,5,15,25,35),labels=monthlabel,label.pos=monthdeg,show.radial.grid=F, mar=c(4,1.5,4.5,3))
    rasterImage(img,-35,-35,35,35)
    polar.plot(icevolume$vol[1:i], polar.pos=icevolume$icedeg[1:i], clockwise=T, start=-20, rp.type="s", point.symbols='.', point.col='blue', radial.lim=c(0,5,15,25,35),radial.labels=c(NA,5,15,25,35),labels=monthlabel,label.pos=monthdeg,show.radial.grid=F, mar=c(4,1.5,4.5,3), add=T)
    polar.plot(icevolume$vol[i:(i+6)], polar.pos=icevolume$icedeg[(i):(i+6)], clockwise=T, start=-20, rp.type="s", point.symbols='o',point.col='red', radial.lim=c(0,5,15,25,35),radial.labels=c(NA,5,15,25,35),labels=monthlabel,label.pos=monthdeg,show.radial.grid=F, add=T)
    title(main=bquote("PIOMAS Arctic Sea Ice Volume (1000s of km"^"3"*"):"~.(year)))
    text(-47,"animation by R. Eric Collins, University of Alaska Fairbanks\ndata from http://psc.apl.washington.edu/wordpress/research/projects/arctic-sea-ice-volume-anomaly/",cex=0.5)
  }

}

for (i in 1:100) {
  par(cex=1.8,cex.axis=1.2,cex.lab=1.2, cex.main=1.2)
	polar.plot(0, 0, clockwise=T, start=-20, rp.type="s", point.symbols='.', point.col='blue', radial.lim=c(0,5,15,25,35),radial.labels=c(NA,5,15,25,35),labels=monthlabel,label.pos=monthdeg,show.radial.grid=F, mar=c(4,1.5,4.5,3))
  rasterImage(img,-35,-35,35,35)
  polar.plot(icevolume$vol, polar.pos=icevolume$icedeg, clockwise=T, start=-20, rp.type="s", point.symbols='.', point.col='blue', radial.lim=c(0,5,15,25,35),radial.labels=c(NA,5,15,25,35),labels=monthlabel,label.pos=monthdeg,show.radial.grid=F, mar=c(4,1.5,4.5,3), add=T)
  polar.plot(icevolume$vol[1:7], polar.pos=icevolume$icedeg[1:7], clockwise=T, start=-20, rp.type="s", point.symbols='o',point.col='red', radial.lim=c(0,5,15,25,35),radial.labels=c(NA,5,15,25,35),labels=monthlabel,label.pos=monthdeg,show.radial.grid=F, add=T)
  polar.plot(icevolume$vol[(dim(icevolume)[1]-7):dim(icevolume)[1]], polar.pos=icevolume$icedeg[(dim(icevolume)[1]-7):dim(icevolume)[1]], clockwise=T, start=-20, rp.type="s", point.symbols='o',point.col='red', radial.lim=c(0,5,15,25,35),radial.labels=c(NA,5,15,25,35),labels=monthlabel,label.pos=monthdeg,show.radial.grid=F, add=T)
  title(main=bquote("PIOMAS Arctic Sea Ice Volume (1000s of km"^"3"*"): 1979--2013"))
  text(-47,"animation by R. Eric Collins, University of Alaska Fairbanks\ndata from http://psc.apl.washington.edu/wordpress/research/projects/arctic-sea-ice-volume-anomaly/", cex=0.5)
}

dev.off()

