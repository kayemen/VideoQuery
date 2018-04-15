from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class Video(Base):
    __tablename__ = 'video'

    vid_id = Column(Integer, primary_key=True)
    video_name = Column(String)
    framecount = Column(Integer)
    avg_brightness = Column(Float)
    perceptual_hash = Column(String)

    frames = relationship("Frame", back_populates='video',
                          order_by='Frame.frame_id')

    def __repr__(self):
        return "<Video %d: video_name='',framecount=%d,avg_brightness=%.3f,hash=%s" % (
            self.vid_id, self.video_name, self.framecount, self.avg_brightness,
            self.perceptual_hash
        )

    def __str__(self):
        return repr(self)


class Frame(Base):
    __tablename__ = 'frame'

    frame_id = Column(Integer, primary_key=True)
    vid_id = Column(Integer, ForeignKey('video.vid_id'))
    frame_index = Column(Integer)
    avg_brightness = Column(Float)
    perceptual_hash = Column(String)

    video = relationship("Video", back_populates='frames')

    def __repr__(self):
        return "<Frame %d: frame_index='%d',avg_brightness=%.3f,hash=%s" % (
            self.frame_id, self.frame_index, self.avg_brightness,
            self.perceptual_hash
        )

    def __str__(self):
        return repr(self)


class Audio(Base):
    __tablename__ = 'audio'


class MultiframeFeatures(Base):
    __tablename__ = 'multi_features'
