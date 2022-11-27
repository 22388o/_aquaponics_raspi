from AquaponicsSystemManager import Class_AquaponicsSystemManager as APSM

if __name__ == "__main__":
    do = APSM.APSystemManager(delta_t_h=-2, heartbeat=20)
    do.start_manager()
