from matplotlib import pyplot as plt
import time
import random

#========== Define Track Classes ============#

class Straight:
	def __init__(self, length):
		self.length = length #0 1 2 - short medium long
		self.type = "STRAIGHT"
		self.next = None

	def add_next(self,next):
		self.next = next

	def next(self):
		return self.next

	def string(self):
		return (["Short","Medium","Long"][self.length] + " Straight")

class Turn:
	def __init__(self, sev, length):
		self.sev = sev #0 1 2 - slow medium fast
		self.length = length #0 1 2 - short medium long
		self.type = "TURN"
		self.next = None

	def add_next(self, next):
		self.next = next

	def next(self):
		return self.next

	def string(self):
		return(["Slow","Medium","Fast"][self.sev] + " Corner " + ["(Short)","(Medium)","(Long)"][self.length])

class Start_finish:
	def __init__(self):
		self.next = None
		self.type = "START/FINISH"

	def string(self):
		return self.type

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

	def add_turn(self, sev, length):
		new_turn = Turn(sev, length)
		new_turn.next = self.start_finish
		self.track_arr[-1].next = new_turn
		self.track_arr.append(new_turn)

#========== Define Driver Classes ===========#




#========== Define Car Classes =============#
class Car:
	def __init__(self, traction, top_speed, downforce, driver_name): #add driver to car here
		self.traction = traction #float 0-1
		self.top_speed = top_speed #float 0-1
		self.downforce = downforce #float 0-1
		self.tyre_wear = None
		self.tyre_type = None
		self.damage = 1.0

		self.driver_name = driver_name	

	def set_tyre(self, tyre):
		self.tyre_type = tyre # 0 1 2 - hard medium soft
		self.tyre_wear = 1.0

	def repair(self):
		repair_val = 1-self.damage
		self.damage = 1.0
		return repair_val


#========= Define Race Classes ===============#
class Race:
	def __init__(self, track, laps):
		self.sim = Sim()
		self.track = track
		self.lap = 0
		self.race_length = laps
		self.race_tracker = []
		self.num_cars = 0
		self.cur_section = track.start_finish
		self.prev_section = None

	def add_car(self, car):
		self.num_cars += 1
		self.race_tracker.append({"car":car, "gap_front":0.5, "gap_leader":0.5*(self.num_cars-1), "speed_mod":0, "downforce_mod":0})
		self.race_tracker[0]["gap_front"] = None

	def reorder(self):
		cumulative_gap = 0
		for place in range(1,self.num_cars):
			cumulative_gap += self.race_tracker[place]["gap_front"]
			self.race_tracker[place]["gap_leader"] = cumulative_gap
		self.race_tracker.sort(key = lambda x: x["gap_leader"])

		prev_gap = 0
		leader_gap_mod = -self.race_tracker[0]["gap_leader"]
		self.race_tracker[0]["gap_front"] = None
		self.race_tracker[0]["gap_leader"] = 0
		for place in range(1,self.num_cars):
			self.race_tracker[place]["gap_leader"] += leader_gap_mod
			self.race_tracker[place]["gap_front"] = self.race_tracker[place]["gap_leader"] - prev_gap
			prev_gap = self.race_tracker[place]["gap_leader"]

	def next(self): #still need to add tyre wear
		if self.lap == self.race_length and self.cur_section.type == "START/FINISH":
			return False

		if self.cur_section.type == "TURN" and self.cur_section.sev == 0:
			if self.prev_section.type == "STRAIGHT" or (self.prev_section.type == "TURN" and self.prev_section.sev == 2):
				pass #BRAKING ZONE ADD HERE 
		
		if self.cur_section.type == "START/FINISH":
			self.lap += 1
		elif self.cur_section.type == "STRAIGHT":
			secs = self.cur_section.length
			if self.prev_section.type == "TURN" and self.prev_section.sev == 0:
				self.sim.calc_modifiers(self.race_tracker)
				self.sim.calc_traction_zone(self.race_tracker)
				self.reorder()
				for i in range (secs):
					self.sim.calc_modifiers(self.race_tracker)
					self.sim.calc_straight(self.race_tracker)
					self.reorder()
			else:
				for i in range (secs + 1):
					self.sim.calc_modifiers(self.race_tracker)
					self.sim.calc_straight(self.race_tracker)
					self.reorder()
		elif self.cur_section.type == "TURN":
			secs = self.cur_section.length
			if self.prev_section.type == "TURN" and self.prev_section.sev == 0 and self.cur_section.sev == 2:
				self.sim.calc_modifiers(self.race_tracker)
				self.sim.calc_traction_zone(self.race_tracker)
				self.reorder()
				for i in range (secs):
					self.sim.calc_modifiers(self.race_tracker)
					self.sim.calc_turn(self.race_tracker, self.cur_section.sev)
					self.reorder()
			else:
				for i in range (secs + 1):
					self.sim.calc_modifiers(self.race_tracker)
					self.sim.calc_turn(self.race_tracker, self.cur_section.sev)
					self.reorder()
		
		self.prev_section = self.cur_section
		self.cur_section = self.cur_section.next
		return True

	def print(self):
		print("Lap " + str(self.lap) + '/' + str(self.race_length))
		print("Current Section: " + self.cur_section.string())
		print("Next Section: " + self.cur_section.next.string())
		for place in range (self.num_cars):
			print(str(place) + ' - ' + self.race_tracker[place]["car"].driver_name + ' - ' + str(round(self.race_tracker[place]["gap_leader"],2)))		

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

		self.max_speed_diff = 1 #max time that can be lost on each section of straight
		self.downforce_penalty = 0.3 #penalty applied to straight line speed for increased downforce
		self.turn_severity_coefficient = [0.3, 0.6, 1] #downforce benefit for slow medium high speed corners
		self.corner_tyre_wear_grip_coefficient = 1 #how much does tyre wear affect cornering
		self.max_turn_diff = 0.5 #max time lost on each section of a corner

	def calc_modifiers(self, race_tracker):
		num_cars = len(race_tracker)
		for place in range(1,num_cars):
			sp_mod = 0
			down_mod = 0
			if race_tracker[place]["gap_front"] < 0.5:
				sp_mod = self.slip_close
				down_mod = self.dirty_air_close				

			elif race_tracker[place]["gap_front"] < 1:
				sp_mod = self.slip_far
				down_mod = self.dirty_air_far

			race_tracker[place]["speed_mod"] = sp_mod
			race_tracker[place]["downforce_mod"] = down_mod

	def calc_traction_zone(self, race_tracker): #add tyre modifier here
		num_cars = len(race_tracker)
		traction_vals = []
		for place in range(0, num_cars):
			car = race_tracker[place]["car"]

			traction = car.traction * car.tyre_wear * self.traction_tyre_wear_coefficient
			
			traction_vals.append(traction)

		for place in range(1, num_cars):
			car = race_tracker[place]["car"]

			time_diff = (traction_vals[place-1] - traction_vals[place])*self.max_traction_diff

			race_tracker[place]["gap_front"]+=time_diff

	def calc_straight(self, race_tracker):
		num_cars = len(race_tracker)
		speed_vals = []

		for place in range(0, num_cars):
			car_dict = race_tracker[place]
			car_speed = car_dict["car"].top_speed + car_dict["speed_mod"]
			car_downforce_penalty = (car_dict["car"].downforce + car_dict["downforce_mod"])*self.downforce_penalty

			speed_vals.append(car_speed - car_downforce_penalty)

		for place in range(1, num_cars):
			time_diff = (speed_vals[place-1] - speed_vals[place])*self.max_speed_diff

			race_tracker[place]["gap_front"]+=time_diff

	def calc_turn(self, race_tracker, sev): #add tyre modifier here
		num_cars = len(race_tracker)
		turn_vals = []
		for place in range(0, num_cars):
			car_dict = race_tracker[place]

			car_downforce = car_dict["car"].downforce + car_dict["downforce_mod"]
			car_grip = car_downforce*self.turn_severity_coefficient[sev]*self.corner_tyre_wear_grip_coefficient*car_dict["car"].tyre_wear
			turn_vals.append(car_grip)


		for place in range(1,num_cars):
			time_diff = (turn_vals[place-1] - turn_vals[place])*self.max_turn_diff

			race_tracker[place]["gap_front"]+=time_diff


#======== Display Functions =============#

def run_race_graph(race):
	num_cars = race.num_cars
	pos_dict = {}
	time_dict = {}
	for i in range(num_cars):
		pos_dict[race.race_tracker[i]["car"].driver_name] = [i]
		time_dict[race.race_tracker[i]["car"].driver_name] = [i*0.5]
	
	while race.next():
		print("Lap " + str(race.lap) + '/' + str(race.race_length), end='\r')
		for i in range(num_cars):
			pos_dict[race.race_tracker[i]["car"].driver_name].append(i)
			time_dict[race.race_tracker[i]["car"].driver_name].append(race.race_tracker[i]["gap_leader"])


	for key in time_dict:
		plt.plot(pos_dict[key])
	plt.show()

	for key in time_dict:
		plt.plot(time_dict[key])

	plt.show()	


#========== Misc Functions ==============#

def random_race():
	track = Track("Test")
	track.add_straight(2)
	track.add_turn(0,1)
	track.add_turn(1,1)
	track.add_straight(1)
	track.add_turn(2,2)
	track.add_straight(0)
	track.add_turn(0,0)
	track.add_straight(1)

	cars = []
	for i in range(50):
		cars.append(Car(random.random(),random.random(),random.random(), "Car"+str(i)))
		cars[-1].set_tyre(0)

	race = Race(track, 100)

	for car in cars:
		race.add_car(car)

	return race

def hungaroring():
	track = Track("Hungaroring")
	track.add_straight(1)
	track.add_turn(0,2)
	track.add_straight(0)
	track.add_turn(0,1)
	track.add_turn(2,0)
	track.add_straight(1)
	track.add_turn(1,0)
	track.add_turn(0,1)
	track.add_straight(0)
	track.add_turn(0,0)
	track.add_straight(0)
	track.add_turn(1,1)
	track.add_turn(0,1)
	track.add_turn(2,0)
	track.add_turn(1,1)
	track.add_straight(0)
	track.add_turn(1,1)
	track.add_straight(0)
	track.add_turn(0,2)
	track.add_straight(0)
	track.add_turn(1,2)
	track.add_straight(0)

	cars = []
	for i in range(50):
		cars.append(Car(random.random(),random.random(),random.random(), "Car"+str(i)))
		cars[-1].set_tyre(0)

	race = Race(track, 100)

	for car in cars:
		race.add_car(car)

	return race

def optimum_downforce(track):
	pass
	#add asdasda here




