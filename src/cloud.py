from CryptoAPI import *


class Cloud:

    def __init__(self):
        self.h_data   = (0, 0)    # id_h, R
        self.p_data   = (0, 0)    # id_p, NID
        self.d_data   = (0, 0, 0) # id_d, id_p, RD
        self.message  = (0,0)    # S2, C1 || S4, C2
        self.database = {}
        self.Sni      = gen_randint()


    def ping_to_hospital(self,hospital):
        print(":: phase 1, step 2 ::")
        id_h, R = self.h_data
        self.id_h = id_h

        x   = gen_randint()
        A   = gen_hash(id_h, R, x)
        S1  = gen_hash(A)
        B   = id_h^x
        print("Send <S1, B> to Hospital via PUBLIC channel")
        # print(f"Send <S1, B> = <{S1}, {B}> to Hospital via PUBLIC channel")
        hospital.c_data = (S1,B)
        self.A = A
        self.B = B
    

    def ping_to_patient(self, patient):
        print(":: phase 2, step 2 ::")
        id_p, NID = self.p_data
        Sig_h   = self.database['Sig_h']
        C_h     = self.database['C_h']
        Sni     = self.Sni

        I   = Sni^NID
        S3  = gen_hash(NID, I, C_h, Sig_h)
        print("Send <I, S3, C_h, Sig_h> to Patient via PUBLIC channel")
        patient.c_data = (I, S3, C_h, Sig_h)

    
    def ping_to_doctor(self, doctor):
        print("phase2, step2")
        id_d, id_p, RD = self.d_data

        SK_dc   = gen_hash(id_d, id_p, RD)
        S5      = gen_hash(SK_dc, Sig)
    

    def receive_and_store_hospital(self):
        print(":: phase 1, step 4 ::")
        id_h, A, B  = self.id_h, self.A, self.B
        S2, C1      = self.message
        SK1_hc      = gen_hash(id_h, A, B)

        if S2 != gen_hash(SK1_hc, C1):
            print("Cannot Authenticate Hospital")
            exit(1)
        
        print("Hospital authenticated")
        id_p, id_d, C_h, Sig_h, NID = decrypt(SK1_hc, C1)
        # print("Data received: ")
        # print(id_p.decode())
        # print(id_d.decode())
        # print(C_h.decode())
        # print(Sig_h.decode())
        # print(NID.decode())
        self.database['id_p']   = id_p
        self.database['C_h']    = C_h
        self.database['Sig_h']  = Sig_h
        self.database['NID']    = NID
        print("Saved Hospital data to database")
    

    def receive_and_store_patient(self):
        print(":: phase 2, step 4 ::")
        S4, C2      = self.message
        Sni         = self.Sni
        id_p, NID   = self.p_data
        id_h        = self.id_h

        SK_pc1      = gen_hash(id_p, NID, Sni)
        C_p, Sig_p  = decrypt(SK_pc1, C2)

        if S4 != gen_hash(SK_pc1, C_p, Sig_p):
            print("Unable to authenticate patient")
            exit(1)
        
        self.database['C_p']    = C_p
        self.database['Sig_p']  = Sig_p
        self.database['Sni']    = Sni
        print("Saved Patient data to database")


    def receive_and_store_doctor(self):
        pass


if __name__ == "__main__":
    # just to test functions
    cloud = Cloud()
    cloud.h_data = (123,23)
    cloud.ping_to_hospital(cloud)