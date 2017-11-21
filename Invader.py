class Invader:
  def __init__(self, pos):
    self.pos = pos
    self.missile = False
    self.bottom = False
  def get_pos(self):
    return self.pos
  def set_pos(self, pos):
    self.pos = pos
  def set_missile(self, pos):
    self.missile = pos
  def get_missile(self):
    return self.missile
  def set_bottom(self, bottom):
    self.bottom = bottom
  def get_bottom(self):
    return self.bottom

