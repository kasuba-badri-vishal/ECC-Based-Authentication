from CryptoAPI import *


class Hospital:

    def __init__(self):
        self.id_h   = 1
        self.NID    = 0
        self.Ni     = 0
        self.id_p   = 0
        self.id_d   = 0
        self.R      = gen_randint()
        self.c_data = (0,0)
        self.m_h    = "patient's report generated by healthcare"
        self.PR_h, self.PU_h = gen_sig_keys()


    def ping_to_cloud(self,cloud):
        print(":: phase 1, step 1 :: Hospital")
        print("Send <ID_h, R> to Cloud via SECURE channel")
        # print(f"Send <ID_h, R> = <{self.id_h}, {self.R}> to Cloud via SECURE channel")
        cloud.h_data = (self.id_h,self.R)
    

    def send_message(self, cloud):
        print(":: phase 1, step 3 :: Hospital")
        S1, B = self.c_data
        id_h, id_p, id_d  = self.id_h, self.id_p, self.id_d
        R, m_h = self.R, self.m_h
        PR_h = self.PR_h

        x1 = B^id_h
        A1 = gen_hash(id_h, R, x1)

        temp = gen_hash(A1)
        if S1 != temp:
            print(f"Unable to verify cloud. hospital S1 = {S1}, temp = {temp}")
            exit(1)

        print("Cloud verified")
        Ni = self.Ni
        NID= self.NID

        SK_hc   = gen_hash(id_h, A1, B)
        key1    = gen_hash(id_p, Ni)
        C_h     = encrypt(key1, [m_h])
        MD_h    = gen_hash(m_h)
        Sig_h   = gen_sig(PR_h, MD_h)
        C1      = encrypt(SK_hc, [id_p, id_d, C_h, Sig_h, NID])
        S2      = gen_hash(SK_hc, C1)

        print("Send message to cloud via PUBLIC channel")
        cloud.message = (S2, C1)