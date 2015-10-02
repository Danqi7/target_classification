import sys
import csv
import random
import math

args = str(sys.argv)

#get the command line arguments
filename = str(sys.argv[1])
trainingsize = int(sys.argv[2])
numtrials = int(sys.argv[3])
verbose = (sys.argv[4] == "1")



Ivyfile = {"GoodGrades":0, "GoodLetters":1, "GoodSAT":2, "IsRich":3, "HasScholarship":4, "ParentAlum":5, "SchoolActivities":6}
Majorityfile = {"bob":0, "sue":1, "larry":2, "dave":3, "alice":4, "john":5}

#parse the input file
examples = list()
with open(filename) as infile:
	reader = csv.DictReader(infile)
	for row in reader:
		if "IvyLeague" in filename:
			line = str(row['GoodGrades \tGoodLetters \tGoodSAT \tIsRich \tHasScholarship \tParentAlum \tSchoolActivities\tCLASS'])
			values = line.split(' \t')
			
		else:
			line = str(row["bob\tsue\tlarry\tdave\talice\tjohn\tCLASS"])
			values = line.split('\t')
		examples.append(values)
		examplenumber = len(examples)
		
ivyattrs = ["GoodGrades", "GoodLetters", "GoodSAT", "IsRich", "HasScholarship", "ParentAlum", "SchoolActivities"]
majoattrs = ["bob", "sue", "larry", "dave", "alice", "john"]

#divide example into training set and testing set
def dividesets(dataset):
	trainset = list()
	testset = list()
	
	i = 0
	testset = dataset[:]
	while i < trainingsize:
		selected = dataset[random.randint(0,len(dataset)-1)]
		if not selected in trainset:
			testset.remove(selected)
			trainset.append(selected)
			i = i + 1
	return [testset, trainset]


#calculate prior probability of the training set

#func distro takes a list containing examples 
#and returns a list contains that number of positive and negative classification
def distro(dataset): 
	neg = 0
	pos = 0
	for item in dataset:
		if item[-1] == "true":
	 		pos = pos + 1
		else:
			neg = neg + 1
	return [pos, neg]



#construct a decision tree based on the training set

#func entropy takes an input dataset and returns the entropy of it
def entropy(dataset):
	result = distro(dataset)
	if result[0] != 0 and result[1] != 0:
		p1 = float(result[0]) / float(len(dataset))
		p2 = float(result[1]) / float(len(dataset))
		entropy = -p1*(math.log(p1,2)) - p2*(math.log(p2,2))
	else:
		entropy = 0
	return entropy


#func split split the input dataset based on the input attribute
#and returns  two sub-dataset respectively corresponding to the value of attribute 
def split(dataset, attr):
	if "IvyLeague" in filename:
		dictionary = Ivyfile
	else:
		dictionary = Majorityfile
	possub = list()
	negsub = list()
	for i in range(len(dataset)):
		if dataset[i][dictionary[attr]] == "true":
			possub.append(dataset[i])
		else:
			negsub.append(dataset[i])
	
	return [possub, negsub]


#func IG returns the information gain of the input dataset 
#after selecting the input attribute
def IG(dataset, attr):
	before = entropy(dataset)
	subs = split(dataset,attr)
	possub = subs[0]
	negsub = subs[1]
	posentro = entropy(possub)
	negentro = entropy(negsub)
	after = float(len(possub))/float(len(dataset)) * posentro + float(len(negsub))/float(len(dataset)) * negentro
	return before-after
	



#define a tree structure
class Tree(object):
	def __init__(self):
		self.left = None
		self.right = None
		self.date = None

#func ID3 takes the training examples, the target concept and attributes of the examples,
#it returns the decision tree based on the training examples
def ID3(examps, attributes):
	root = Tree()
	classdis = distro(examps)
	if classdis[0] == len(examps): #if all examples are positive
		root.data = "true"
		return root
	if classdis[1] == len(examps): #if all examples are negative
		root.data = "false"		
		return root
	if len(attributes) == 0: #if attributes is empty, return the root with most common value
		if classdis[0] > classdis[1]:
			root.data = "true"
		else:
			root.data = "false"
		return root
	
	#computes the best attribute with the largest information gain
	maxig = -10
	for i in range(len(attributes)):
		currentig = IG(examps, attributes[i])
		if currentig > maxig:
			maxig = currentig
			bestattr = attributes[i]
	
	root.data = bestattr

	subs = split(examps, bestattr)
	attributes.remove(bestattr)

	
	if classdis[0] > classdis[1]:
		mode = "true"
	else:
		mode = "false"
	
	if len(subs[0]) > 0:
		root.left = ID3(subs[0],attributes)
	else:
		root.left = mode
	if len(subs[1]) > 0:
		root.right = ID3(subs[1],attributes)
	else:
		root.right = mode
		
	return root


#classify one single testing example
def classhelper(examp, root):
	if root.data == "true":
		return "true"
	if root.data == "false":
		return "false"
		
	if "IvyLeague" in filename:
		dictionary = Ivyfile
	else:
		dictionary = Majorityfile	

	if examp[dictionary[root.data]] == "true":
			return classhelper(examp, root.left)
	else:
			return classhelper(examp, root.right)
	

#classify the examples using decision tree
def classifyID3(dataset, root):
	result = list()

	for i in range(len(dataset)):
		value = classhelper(dataset[i], root)
		result.append(value)

	return result

#classify examples using prior probabilities
def classifyPP(dataset):
	result = distro(dataset)
	pos = result[0]
	neg = result[1]
	return float(pos) / float((pos+neg))


#determine the portion of correct classifications
def portionID3(testset, tree):
	correct = 0
	output = classifyID3(testset,tree)
	for i in range(len(output)):
		if testset[i][-1] == output[i]:
			correct = correct + 1
	
	return float(correct)/float(len(testset))
	
def portionPP(testset):
	return classifyPP(testset)

#returns the decision tree structure
def treestructure(root):
	result = list()
	if root != None:
		print "Parent: {0}".format(root.data)
		if root.left != None:
			print "Leftchid: {0}".format(root.left.data)
		if root.right != None:
			print "Leftchid: {0}".format(root.right.data)
		treestructure(root.left)
		treestructure(root.right)


for i in range(1):
	if "IvyLeague" in filename:
		attributes = ivyattrs
	else:
		attributes = majoattrs

	sets = dividesets(examples)
	tree = ID3(sets[1],attributes)
	treestructure(tree)
	print "Percent of test cases correctly classified by a decision tree built with ID3 = {0}".format(portionID3(sets[0],tree))
	print "Percent of test cases correctly classified by prior probabolity = {0}".format(portionPP(sets[0]))

	if verbose == 1:
		print "Fileused: {0}".format(filename)
		print "Size of training data: {0}".format(len(sets[1]))
		print "Size of testing data: {0}".format(len(sets[0]))
	
	
	





			
		
		





	
	
	
		
	
	







	


	



	

		
	


	








