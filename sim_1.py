#========== Define Track Classes ============#

class Straight:
	def __init__(self, length):
		self.length = length #1 2 3 - short medium long
		self.type = "STRAIGHT"
		self.next = None

	def add_next(self,next):
		self.next = next

	def next(self):
		return self.next

class Turn:
	def __init__(self, sev, length):
		self.sev = sev #1 2 3 - slow medium fast
		self.length = length #1 2 3 - short medium long
		self.type = "TURN"
		self.next = None

	def add_next(self, next):
		self.next = next

	def next(self):
		return self.next

class Start_finish:
	def __init__(self):
		self.next = None

class Track:
	def __init__(self, name):
		self.name = name
		self.start_finish = Start_finish()
		self.track_arr = [self.start_finish]

	def add_straight(self, length):
		new_straight = Straight(length)
		new_straight.next = self.start_finish
		self.track_arr[-1].next = new_straight
		self.track_arr.append(new_straight)

	def add_turn(self, sev, lengthh)
		new_turn = Turn(sev, length)
		new_turn.next = self.start_finish
		self.track_arr[-1].next = new_turn
		self.track_arr.append(new_turn)

#========== Define Driver Classes ===========#




#========== Define Car Classes =============#
class Car:
	def __init__(self, traction, top_speed, downforce) #add driver to car here
		self.traction = traction #float 0-1
		self.top_speed = top_speed #float 0-1
		self.downforce = downforce #float 0-1
		self.tyre_wear = None
		self.tyre_type = None
		self.damage = 1.0

	def set_tyre(tyre):
		self.tyre_type = tyre # 1 2 3 - hard medium soft
		self.tyre_wear = 1.0

	def repair():
		repair_val = 1-self.damage
		self.damage = 1.0
		return repair_val


#========= Define Race Classes ===============#
class Race:
	def __init__(self, track, laps):
		self.sim = Sim()
		self.track = track
		self.laps = laps
		self.race_tracker = []
		self.num_cars = 0

	def add_car(self, car):
		self.num_cars += 1
		self.cars.append({"car":car, "gap_front":0.5, "gap_leader":0.5*(num_cars-1), "speed_mod":0, "downforce_mod":0})
		self.cars[0]["gap_front"] = None

	def reorder(self):
		cumulative_gap = 0
		for place in range(1,self.num_cars):
			cumulative_gap += self.race_tracker[place]["gap_front"]
			self.race_tracker[place]["gap_leader"] = cumulative_gap
		self.race_tracker.sort(key = lambda x: x["gap_leader"])

		prev_gap = 0
		leader_gap_mod = -self.race_tracker[0]["gap_leader"]
		self.race_tracker[0]["gap_front"] = None
		for place in range(1,self.num_cars):
			self.race_tracker[place]["gap_leader"] += leader_gap_mod
			self.race_tracker[place]["gap_front"] = self.race_tracker[place]["gap_leader"] - prev_gap
			prev_gap = self.race_tracker[place]["gap_leader"]


#========== Simulation Settings =============#

#For now just hard code it all here
class Sim:
	def __init__(self):
		self.max_repair = 30 #repair time = damage amount * max repair

		self.slip_close = 0.2 #speed bonus for close slipstream
		self.slip_far = 0.1 #speed bonus for further slip stream
		self.dirty_air_close = -0.2 #downforce penalty for close dirty air
		self.dirty_air_far = -0.1 #downforce penalty for far dirty air
		
		self.traction_tyre_wear_coefficient = 1 #traction = traction_val * tyre_wear * coefficient
		self.max_traction_diff = 0.75 #max time that can be lost through lack of traction

	def calculate_modifiers(self, race_tracker):
		num_cars = len(race_tracker)
		for place in range(1,num_cars):
			sp_mod = 0
			down_mod = 0
			if race_tracker[place]["gap_front"] < 0.5:
				sp_mod = self.slip_close
				down_mod = self.dirt_air_close				

			elif race_tracker[place]["gap_front"] < 1:
				sp_mod = self.slip_far
				down_mod = self.dirty_air_far

			race_tracker[place]["speed_mod"] = sp_mod
			race_tracker[place]["downforce_mod"] = down_mod

	def calc_traction_zone(self, race_tracker): #passing dicts from race_tracker
		num_cars = len(race_tracker)
		for place in range(1,num_cars):
			car_ahead = race_tracker[place-1]["car"]
			car_behind = race_tracker[place]["car"]

			traction_diff = (car_ahead.traction*car_ahead.tyre_wear -  car_behind.traction*car_behind.tyre_wear)*self.traction_tyre_wear_coefficient
			time_diff = traction_diff*self.max_traction_diff

			race_tracker[place]["gap_front"]+=time_diff




			







