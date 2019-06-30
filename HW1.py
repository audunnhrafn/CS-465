
#Programming assignment 1
#CS-465 Introduction to Cybersecurity
#Audunn Hrafn Alexandersson
#Login ID: aha0026
#WVU ID: 800-267530
#2/12/2018
#
# Program should be fully functional while we have both a key.txt and input.txt file in the working directory.


#These are constants for the files for easier access.
INPUT_FILE_NAME = "input.txt"
KEY_FILE_NAME = "key.txt"
OUTPUT_FILE_NAME = "output.txt"


#Gets the input from input file
def getInput():
    text = ""
    with open(INPUT_FILE_NAME) as file:
        for line in file:
            text += line
    text = text.replace(" ", "").replace(".", "").replace(",", "").replace("\n", "")  # removes unwanted chars and spaces

    return text


#Write string and name into file for the Preprocessing and Substitution part.
def writeLine(text, name):
    output = name + "\n" + text + "\n" + "\n" #This is done to get correct format

    with open(OUTPUT_FILE_NAME, "a") as file:
        file.write(output)


#Substitues letters using Vigenere cipher rules
def substitute(text):
    textList = list(text)
    keyList = []
    returnStr = ""

    with open(KEY_FILE_NAME) as file: #get the Key
        for string in file:
            for char in string:
                keyList.append(char)

    while len(keyList) <= len(textList):
        keyList.extend(keyList) #If the key is shorter than text then add key to it self

    for i in range(0,len(textList)):
        #Pluses correct letter value and key value then modulo with 26 to find the correct Vigenere cipher letter
        ViCiLetter = ((ord(textList[i]) - 65) + (ord(keyList[i]) - 65)) % 26
        returnStr += chr(ViCiLetter + 65)
    return returnStr


#Appends the letter A to make the length divisible by 16
def padding(text):
    padChars = 16 - (len(text) % 16) #Gets how many padding chars are needed
    text += (padChars * "A")
    return text


#Writes to output file Padding and ShiftRows in correct format
def writeBox(text, name):
    output = name + "\n"
    counter = 0
    for i in range(0,len(text), 4):
        output += text[counter] + " "
        output += text[counter+1] + " "
        output += text[counter+2] + " "
        output += text[counter+3] + " " + "\n"
        counter += 4
        if counter % 16 == 0:
            output += "\n"

    with open(OUTPUT_FILE_NAME, "a") as file:
        file.write(output)


#Shifts the rows according to AES encryption rules
def shiftRows(text):
    output = ""
    counter = 0
    lis = [text[i:i+4] for i in range(0, len(text), 4)] #Makes a list with four letters each item

    for i in range(0, len(lis), 4):
        output += lis[counter] #First row
        counter += 1
        output += lis[counter][1:] + lis[counter][0] #Second row
        counter += 1
        output += lis[counter][2:] + lis[counter][0:2] #Third row
        counter += 1
        output += lis[counter][3:] + lis[counter][0:3] #Fourth row
        counter += 1

    return output


#Takes the string and removes every new line
def removeNewLine(text):
    text = text.replace("\n", "")
    return text


#Sets the MSB as 1 or 0 depending on how many ones are in the binary string
def parityBit(text):
    outputList = []

    for char in text:
        binary = "{0:b}".format(ord(char))
        ones = binary.count("1") #counts the ones in the binary string
        if ones % 2 != 0:
            binary = "1" + binary
        else:
            binary = "0" + binary
        hexNum = hex(int(binary, 2)) #get the hex number for the binary string
        outputList.append(removeHex(hexNum))

    return outputList


#Removes the 0x in front of hex strings
def removeHex(hexText):
    hexText = hexText.replace("0x", "")
    return hexText


#Uses the Mix Columns step from AES encryption to mix the columns
def mixColumns(text):
    counter = 0
    lis = text
    a0List,a1List,a2List,a3List = [],[],[],[]

    for i in range(0, len(lis), 4):
        #Gets the binary numbers
        c0 = getBin(lis[counter])
        c1 = getBin(lis[counter+4])
        c2 = getBin(lis[counter+8])
        c3 = getBin(lis[counter+12])
        counter += 1
        #Goes to the next 4x4 matrixi
        if counter % 4 == 0:
            counter += 12
        #Matrix multiplication rules
        a0 = int(RGF_mul(c0, 2),2) ^ int(RGF_mul(c1,3),2) ^ int(c2,2) ^ int(c3, 2)   #First column
        a1 = int(c0, 2) ^ int(RGF_mul(c1, 2),2) ^ int(RGF_mul(c2, 3),2) ^ int(c3, 2) #Second column
        a2 = int(c0, 2) ^ int(c1, 2) ^ int(RGF_mul(c2, 2),2) ^ int(RGF_mul(c3, 3),2) #Third column
        a3 = int(RGF_mul(c0, 3),2) ^ int(c1,2) ^ int(c2, 2) ^ int(RGF_mul(c3, 2),2)  #Fourth column

        #appends them to keep them while we go onto the next one
        a0List.append(removeHex(str(hex(a0))))
        a1List.append(removeHex(str(hex(a1))))
        a2List.append(removeHex(str(hex(a2))))
        a3List.append(removeHex(str(hex(a3))))
    #combines all the lists to get the correct order
    output = combineLists(a0List, a1List, a2List, a3List)
    return output


#Multiplication of 8 bit number
def RGF_mul(num, multi):
    #Shifting << 1
    one = num[1:] + "0"

    #If we want 3x multiplication instead of only 2
    if multi == 3:
        #XOR original and the shifted one
        b = int(one, 2) ^ int(num, 2)
        b = '{0:b}'.format(b).zfill(8)
    else:
        b = str(one)

    #If MSB is one then we have to XOR with 00011011
    if num[0] == "1":
        b = int(b, 2) ^ int("00011011", 2)
    else:
        b = int(b,2)

    return '{0:b}'.format(b).zfill(8)


#Takes the a0-a3 lists and combines them for correct order
def combineLists(one, two, three, four):
    counter = 0
    output = []

    for i in range(0, len(one), 4):
        output.append(one[counter:counter+4])
        output.append(two[counter:counter+4])
        output.append(three[counter:counter+4])
        output.append(four[counter:counter+4])
        counter += 4

    output = [item for sublist in output for item in sublist]
    return output


#Gets the binary number
def getBin(hex):
    return bin(int(hex, 16))[2:].zfill(8)


#Writes out to the output file for Parity and MixColumns in hex
def writeHex(text, name):
    counter = 0
    output = name + "\n"

    for i in text:
        output += i + " "
        counter += 1
        if counter % 4 == 0:
            output += "\n"
        if counter % 16 == 0:
            output += "\n"

    with open(OUTPUT_FILE_NAME, "a") as file:
        file.write(output)


if __name__ == "__main__":
    #Preprocessing
    text = getInput()
    writeLine(text, "Preprocessing:")

    #Substitution
    text = substitute(text)
    writeLine(text, "Substitution:")

    #Padding
    text = padding(text)
    writeBox(text, "Padding:")

    #Shift Rows
    text = shiftRows(text)
    writeBox(text, "ShiftRows:")

    #Parity bit
    text = removeNewLine(text)
    text = parityBit(text)
    writeHex(text, "Parity:")

    #Mixed Columns
    mixCol = mixColumns(text)
    writeHex(mixCol, "MixColumns:")
