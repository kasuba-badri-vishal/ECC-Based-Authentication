from CryptoAPI import *


class Cloud:

    def __init__(self):
        self.h_data     = (0, 0)    # id_h, R
        self.p_data     = (0, 0)    # id_p, NID || id_p, id_d, Sni
        self.d_data     = (0, 0, 0) # id_d, id_p, RD
        self.message    = (0,0)    # S2, C1 || S4, C2 || S9, C5
        self.database   = {}
        self.Sni        = gen_randint()
        self.SK_dc      = 0
        self.SK_pc1     = 0


    def ping_to_hospital(self,hospital):
        print(":: phase 1, step 2 :: Cloud")
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
        print(":: phase 2, step 2 :: Cloud")
        id_p, NID = self.p_data
        Sig_h   = self.database['Sig_h']
        C_h     = self.database['C_h']
        Sni     = self.Sni

        I   = Sni^NID
        S3  = gen_hash(NID, I, C_h, Sig_h)
        print("Send <I, S3, C_h, Sig_h> to Patient via PUBLIC channel")
        patient.c_data = (I, S3, C_h, Sig_h)

    
    def ping_to_doctor(self, doctor):
        print(":: phase 3, step 2 :: Cloud")
        id_d, id_p, RD = self.d_data
        Sig_h   = self.database['Sig_h']
        Sig_p   = self.database['Sig_p']
        C_p     = self.database['C_p']

        SK_dc   = gen_hash(id_d, id_p, RD)
        self.SK_dc = SK_dc
        S5      = gen_hash(SK_dc, Sig_h, Sig_p, C_p)
        C3      = encrypt(SK_dc, [Sig_h, Sig_p, C_p])
        print("Send <S5, C3> to Doctor via PUBLIC channel")
        doctor.c_data = (S5, C3)
    

    def receive_and_store_hospital(self):
        print(":: phase 1, step 4 :: Cloud")
        id_h, A, B  = self.id_h, self.A, self.B
        S2, C1      = self.message
        SK1_hc      = gen_hash(id_h, A, B)

        if S2 != gen_hash(SK1_hc, C1):
            print("Cannot Authenticate Hospital")
            exit(1)
        
        print("Hospital authenticated")
        id_p, id_d, C_h, Sig_h, NID = decrypt(SK1_hc, C1)
        self.database['id_p']   = id_p
        self.database['C_h']    = C_h
        self.database['Sig_h']  = Sig_h
        self.database['NID']    = NID
        print("Saved Hospital data to database")
    

    def receive_and_store_patient(self):
        print(":: phase 2, step 4 :: Cloud")
        S4, C2      = self.message
        Sni         = self.Sni
        id_p, NID   = self.p_data
        id_h        = self.id_h

        SK_pc1      = gen_hash(id_p, NID, Sni)
        self.SK_pc1  = SK_pc1
        C_p, Sig_p  = decrypt(SK_pc1, C2)

        if S4 != gen_hash(SK_pc1, C_p, Sig_p):
            print("Unable to authenticate patient")
            exit(1)
        
        self.database['C_p']    = C_p
        self.database['Sig_p']  = Sig_p
        self.database['Sni']    = Sni
        print("Saved Patient data to database")


    def receive_and_store_doctor(self):
        print(":: phase 3, step 4 :: Cloud")
        S6, C4 = self.message
        SK_dc  = self.SK_dc


        C_d, Sig_d  = decrypt(SK_dc, C4)

        if S6 != gen_hash(SK_dc, C_d, Sig_d):
            print("Cannot authenticate Doctor ")
            exit(1)
        print("Doctor authenticated")

        self.database['C_d']    = C_d
        self.database['Sig_d']  = Sig_d
        print("Saved Doctor data to database")
    

    def ping_download_request(self, patient):
        print(":: phase 4, step 2:: Cloud")
        id_p, id_d, Sni = self.p_data
        # check database record using id_p, id_d, Sni
        NID     = self.database['NID']
        C_d     = self.database['C_d']
        Sig_d   = self.database['Sig_d']
        SK_pc1  = gen_hash(id_p, NID, Sni)

        S8      = gen_hash(SK_pc1, C_d, Sig_d)
        print("Send <S8, C_d, Sig_d> to Patient via PUBLIC channel")
        patient.c_data = (S8, C_d, Sig_d)


    def save_patient_data(self):
        print(":: phase 4, step 4 :: Cloud")
        S9, C5  = self.message
        SK_pc1  = self.SK_pc1

        if S9 != gen_hash(SK_pc1, C5):
            print("Unable to verify Patient")
            exit(1)
        print("Patient verified")

        self.database['C5'] = C5
        print("Saved patient data to database")
        print("Decryption key lies with patient")
        print("SUCCESS! completed TMIS transaction using Li et al. Protocol")



if __name__ == "__main__":
    # just to test functions
    cloud = Cloud()
    cloud.h_data = (123,23)
    cloud.ping_to_hospital(cloud)