import socket
import sys
from robodk import robolink, robomath

ROBOT_IP   = "192.168.0.1"
ROBOT_PORT = 8888
BUFFER_SIZE = 1024

#---------------------------------------------------------------------------------
# Set the minimum number of degrees of freedom that are expected
nDOFs_MIN = 6

# Set the driver version
DRIVER_VERSION = "RoboDK Driver for Arctos v0.0.1"

# RDK = robolink.Robolink()
# ROBOT = RDK.Item('Arctos', robolink.ITEM_TYPE_ROBOT)

socket_robot = None  # Socket global para mantener conexión persistente

# Función auxiliar para recibir respuesta completa
def recv_full_response(sock):
    response = ""
    sock.settimeout(2.0)
    try:
        while True:
            part = sock.recv(BUFFER_SIZE).decode(errors='ignore')
            response += part
            if 'ok' in response.lower() or 'error' in response.lower():
                break
    except socket.timeout:
        pass
    return response.strip()

# Conexión persistente al iniciar RoboDK
def Connect(params=None):
    global socket_robot
    socket_robot = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_robot.settimeout(3.0)
    try:
        socket_robot.connect((ROBOT_IP, ROBOT_PORT))
        socket_robot.sendall(b"?\n")
        resp = recv_full_response(socket_robot)
        if 'ok' in resp.lower():
            print(f"[Arctos_Driver] Conectado exitosamente a {ROBOT_IP}:{ROBOT_PORT}")
            return True
        else:
            print(f"[Arctos_Driver] Fallo en respuesta inicial: {resp}")
            socket_robot.close()
            return False
            
    except Exception as e:
        print(f"[Arctos_Driver] Error al conectar: {e}")
        socket_robot.close()
        return False

# Cierre de conexión cuando se desconecta
def Disconnect():
    global socket_robot
    if socket_robot:
        socket_robot.close()
        socket_robot = None
        print("[Arctos_Driver] Desconectado correctamente.")

# Envío de comandos manteniendo conexión abierta
def SendRobotCommand(cmd):
    global socket_robot
    if not socket_robot:
        print("[Arctos_Driver] Socket no conectado.")
        return False
    try:
        socket_robot.sendall((cmd.strip() + "\n").encode())
        resp = recv_full_response(socket_robot)
        print(f"[Arctos_Driver] ► Enviado: {cmd} ─ Recibido: {resp}")
        return 'ok' in resp.lower()
    except Exception as e:
        print(f"[Arctos_Driver] Error al enviar comando '{cmd}': {e}")
        return False

# Movimientos tipo Joint (G0 con ejes A-F)
def MoveJ(joints):
    parts = ["G90", "G0"]
    names = ['X', 'Y', 'Z', 'A', 'B', 'C']
    for i, ang in enumerate(joints[:6]):
        parts.append(f"{names[i]}{ang:.3f}")
    return SendRobotCommand(" ".join(parts))

# Movimientos lineales (X,Y,Z,R,P,W)
def MoveL(pose_rpw):
    # x, y, z, r, p, w = robomath.pose_2_xyzrpw(pose)
    x, y, z, r, p, w = pose_rpw[:6]
    cmd = f"G90 G1 X{x:.3f} Y{y:.3f} Z{z:.3f} R{r:.3f} P{p:.3f} W{w:.3f}"
    return SendRobotCommand(cmd)
    
    

def print_message(message):
    """print_message will display a message in the log window (and the connexion status bar)"""
    print("SMS:" + message)
    sys.stdout.flush() # very useful to update RoboDK as fast as possible

def show_message(message):
    """show_message will display a message in the status bar of the main window"""
    print("SMS2:" + message)
    sys.stdout.flush() # very useful to update RoboDK as fast as possible

def print_joints(joints, ismoving = False):
    #if len(joints) > 6:
    #    joints = joints[0:6]
    if ismoving:
        # Display the feedback of the joints when the robot is moving
        if ROBOT_MOVING:
            print("JNTS_MOVING " + " ".join(format(x, ".5f") for x in joints)) # if joints is a list of float
            #print("JNTS_MOVING " + joints)
    else:
        print("JNTS " + " ".join(format(x, ".5f") for x in joints)) # if joints is a list of float
        #print("JNTS " + joints)
    sys.stdout.flush() # very useful to update RoboDK as fast as possible    


# ---------------------------------------------------------------------------------
# Constant values to display status using UpdateStatus()
ROBOTCOM_UNKNOWN                = -1000
ROBOTCOM_CONNECTION_PROBLEMS    = -3
ROBOTCOM_DISCONNECTED           = -2
ROBOTCOM_NOT_CONNECTED          = -1
ROBOTCOM_READY                  =  0
ROBOTCOM_WORKING                =  1
ROBOTCOM_WAITING                =  2


# Last robot status is saved
global STATUS
STATUS = ROBOTCOM_DISCONNECTED

# UpdateStatus will send an appropriate message to RoboDK which will result in a specific coloring
# for example, Ready will be displayed in green, Waiting... will be displayed in Yellow and other messages will be displayed in red
def UpdateStatus(set_status=None):
    global STATUS
    if set_status is not None:
        STATUS = set_status
        
    if STATUS == ROBOTCOM_CONNECTION_PROBLEMS:
        print_message("Connection problems")
    elif STATUS == ROBOTCOM_DISCONNECTED:
        print_message("Disconnected")
    elif STATUS == ROBOTCOM_NOT_CONNECTED:
        print_message("Not connected")
    elif STATUS == ROBOTCOM_READY:
        print_message("Ready")
    elif STATUS == ROBOTCOM_WORKING:
        print_message("Working...")
    elif STATUS == ROBOTCOM_WAITING:
        print_message("Waiting...")
    else:
        print_message("Unknown status");

# Sample set of commands that can be provided by RoboDK of through the command line
def TestDriver():
    #try:
    #rob_ip = input("Enter the robot IP: ")
    #rob_port = input("Enter the robot Port (default=1101): ")
    #rob_port = int(rob_port)
    rob_ip = 'localhost'
    rob_port = 7000
    
    #RunCommand("CONNECT 192.168.0.100 10000")
    RunCommand("CONNECT %s %s" % (rob_ip, rob_port))
    print("Requesting current joints...\nCJNT")
    #RunCommand("CJNT")
    print("Tip: Type 'CJNT' to retrieve")
    print("Tip: Type 'MOVJ j1 j2 j3 j4 j5 j6' to move the robot (provide joints as angles)")
    #except Exception as e:
    #    print(e)        
        
    #input("Test comands finished. Press enter to continue")
    
    #RunCommand("SETTOOL -0.025 -41.046 50.920 60.000 -0.000 90.000")
    #RunCommand("MOVJ -5.362010 46.323420 20.746290 74.878840 -50.101680 61.958500")
    #RunCommand("SPEED 250")
    #RunCommand("MOVL 0 0 0 0 0 0 -5.362010 50.323420 20.746290 74.878840 -50.101680 61.958500")
    #RunCommand("PAUSE 2000") # Pause 2 seconds

#-------------------------- Main driver loop -----------------------------
# Read STDIN and process each command (infinite loop)
# IMPORTANT: This must be run from RoboDK so that RoboDK can properly feed commands through STDIN
# This driver can also be run in console mode providing the commands through the console input
def RunDriver():
    for line in sys.stdin:
        RunCommand(line)
        
# Each line provided through command line or STDIN will be processed by RunCommand    
def RunCommand(linecmd):
    global ROBOT_IP
    global ROBOT_PORT
    global ROBOT
    global ROBOT_MOVING
    
    # strip a line of words into a list of numbers
    def line_2_values(words):
        values = []        
        for word in words:
            try:
                number = float(word)
                values.append(number)
            except:
                pass
        return values
    
    linecmd = linecmd
    words = linecmd.split(' ')
    values = line_2_values(words)
    nvalues = len(values)
    nwords = len(words)
    received = None
    
    if linecmd == "":
        # Skip if no command is provided
        return
    
    elif nwords >= 2 and linecmd.startswith("CONNECT"):
        # Connect to robot provided the IP and the port
        UpdateStatus(ROBOTCOM_WORKING)
        ROBOT_IP = words[1]
        if nwords >= 3 and nvalues >= 1:
            ROBOT_PORT = int(values[0])
            
        if Connect():
            UpdateStatus(ROBOTCOM_READY)
    
    elif nvalues >= nDOFs_MIN and linecmd.startswith("MOVJ"):
        UpdateStatus(ROBOTCOM_WORKING)
        # Activate the monitor feedback
        ROBOT_MOVING = True        
        # Execute a joint move. RoboDK provides j1,j2,...,j6,x,y,z,w,p,r
        joints = values[0:nvalues]
        if MoveJ(joints):
            # Notify that we are done with this command
            UpdateStatus(ROBOTCOM_READY)
        
    elif nvalues >= nDOFs_MIN and linecmd.startswith("MOVL"):
        UpdateStatus(ROBOTCOM_WORKING)
        # Activate the monitor feedback
        ROBOT_MOVING = True        
        # Execute a linear move. RoboDK provides j1,j2,...,j6,x,y,z,w,p,r
        xyzwpr = values[6:12]
        if MoveL(xyzwpr):
            UpdateStatus(ROBOTCOM_READY)                
                
    elif nvalues >= 2*(nDOFs_MIN+6) and linecmd.startswith("MOVC"):
        UpdateStatus(ROBOTCOM_WORKING)
        # Activate the monitor feedback
        ROBOT_MOVING = True        
        # Execute a circular move. RoboDK provides j1,j2,...,j6,x,y,z,w,p,r
        xyzwpr12 = values[-12:]
        if ROBOT.SendCmd(MSG_MOVEC, xyzwpr12):
            # Wait for command to be executed
            if ROBOT.recv_acknowledge():
                # Notify that we are done with this command
                UpdateStatus(ROBOTCOM_READY)              
        
    elif linecmd.startswith("CJNT"):
        UpdateStatus(ROBOTCOM_WORKING)
        # Retrieve the current position of the robot
        if ROBOT.SendCmd(MSG_CJNT):
            jnts = ROBOT.recv_array()
            print_joints(jnts)

    elif nvalues >= 1 and linecmd.startswith("SPEED"):
        UpdateStatus(ROBOTCOM_WORKING)
        # First value is linear speed in mm/s
        # IMPORTANT! We should only send one "Ready" per instruction
        speed_values = [-1,-1,-1,-1]
        for i in range(max(4,len(values))):
            speed_values[i] = values[i]
            
        #speed_values[0] = speed_values[0] # linear speed in mm/s
        #speed_values[1] = speed_values[1] # joint speed in mm/s
        #speed_values[2] = speed_values[2] # linear acceleration in mm/s2
        #speed_values[3] = speed_values[3] # joint acceleration in deg/s2
        
        if ROBOT.SendCmd(MSG_SPEED, speed_values):
            # Wait for command to be executed
            if self.recv_acknowledge():
                # Notify that we are done with this command
                UpdateStatus(ROBOTCOM_READY)   
            
    elif nvalues >= 6 and linecmd.startswith("SETTOOL"):
        UpdateStatus(ROBOTCOM_WORKING)
        # Set the Tool reference frame provided the 6 XYZWPR values by RoboDK
        if ROBOT.SendCmd(MSG_SETTOOL, values):
            # Wait for command to be executed
            if self.recv_acknowledge():
                # Notify that we are done with this command
                UpdateStatus(ROBOTCOM_READY)   
            
    elif nvalues >= 1 and linecmd.startswith("PAUSE"):
        UpdateStatus(ROBOTCOM_WAITING)
        # Run a pause
        if ROBOT.SendCmd(MSG_PAUSE, values[0]):
            # Wait for command to be executed
            if self.recv_acknowledge():
                # Notify that we are done with this command
                UpdateStatus(ROBOTCOM_READY)   
    
    elif nvalues >= 1 and linecmd.startswith("SETROUNDING"):
        # Set the rounding/smoothing value. Also known as ZoneData in ABB or CNT for Fanuc
        if ROBOT.SendCmd(MSG_ROUNDING, values[0]):
            # Wait for command to be executed
            if ROBOT.recv_acknowledge():
                # Notify that we are done with this command
                UpdateStatus(ROBOTCOM_READY)   
        
    elif nvalues >= 2 and linecmd.startswith("SETDO"):
        UpdateStatus(ROBOTCOM_WORKING)
        #dIO_id = values[0]
        #dIO_value = values[1]
        if ROBOT.SendCmd(MSG_SETDO, values[0:2]):
            # Wait for command to be executed
            if ROBOT.recv_acknowledge():
                # Notify that we are done with this command
                UpdateStatus(ROBOTCOM_READY)     
        
    elif nvalues >= 2 and linecmd.startswith("WAITDI"):
        UpdateStatus(ROBOTCOM_WORKING)
        #dIO_id = values[0]
        #dIO_value = values[1]
        if ROBOT.SendCmd(MSG_WAITDI, values[0:2]):
            # Wait for command to be executed
            if ROBOT.recv_acknowledge():
                # Notify that we are done with this command
                UpdateStatus(ROBOTCOM_READY)            
        
    elif nvalues >= 1 and nwords >= 3 and linecmd.startswith("RUNPROG"):
        UpdateStatus(ROBOTCOM_WORKING)
        ROBOT.SendCmd(MSG_RUNPROG)
        prog_id = values[0] # Program ID is extracted automatically if the program name is Program ID
        prog_name = words[2] # "Program%i" % prog_id
        ROBOT.send_int(prod_id)
        ROBOT.send_line(prog_name)
        # Wait for the program call to complete
        if ROBOT.recv_acknowledge():
            # Notify that we are done with this command
            UpdateStatus(ROBOTCOM_READY)
        
    elif nwords >= 2 and linecmd.startswith("POPUP "):
        UpdateStatus(ROBOTCOM_WORKING)
        message = linecmd[6:]            
        ROBOT.send_line(message)
        # Wait for command to be executed
        if ROBOT.recv_acknowledge():
            # Notify that we are done with this command
            UpdateStatus(ROBOTCOM_READY)
        
    elif linecmd.startswith("DISCONNECT"):
        # Disconnect from robot
        ROBOT.SendCmd(MSG_DISCONNECT)
        ROBOT.recv_acknowledge()
        ROBOT.disconnect()
        UpdateStatus(ROBOTCOM_DISCONNECTED)
                
    elif linecmd.startswith("QUIT"):
        # Stop the driverç
        ROBOT.SendCmd(MSG_DISCONNECT)
        ROBOT.disconnect()
        UpdateStatus(ROBOTCOM_DISCONNECTED)
        quit(0) # Stop the driver
        
    elif linecmd.startswith("t"):
        # Call custom procedure for quick testing
        TestDriver()
        
    else:
        print("Unknown command: " + linecmd)
    
    
    if received is not None:
        UpdateStatus(ROBOTCOM_READY)
    # Stop monitoring feedback
    ROBOT_MOVING = False

if __name__ == "__main__":
    """Call Main procedure"""
    
    if False:
        # Prueba rápida standalone (sin cerrar conexión)
        if Connect():
            SendRobotCommand("G91")          # Incremental
            SendRobotCommand("G0 X10 Y0 Z0") # Movimiento simple
            Disconnect()
        else:
            print("No se pudo conectar en standalone.")
            
    # It is important to disconnect the robot if we force to stop the process
    import atexit
    atexit.register(Disconnect)
    
    # Flush Disconnected message
    print_message(DRIVER_VERSION)
    UpdateStatus()
    
    # Run the driver from STDIN
    RunDriver()
    
    # Test the driver with a sample set of commands
    #TestDriver()





