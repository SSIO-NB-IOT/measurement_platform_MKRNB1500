import csv

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sql.models import Base,Mission,Campaign


class SQLEndpoint():

    def __init__(self,url:str,base_class):
        self.engine = create_engine(url)
        self.base_class = base_class
        Session = sessionmaker()
        self.session = Session.configure(bind=self.engine)
        self.session = Session()

    def init_data_base(self):
        self.base_class.metadata.create_all(self.engine)

    def add_mission(self,mission: Mission,campaign:Campaign):
        campaign.missions.append(mission)
        mission.campaign = campaign
        self.session.add(mission)
        self.session.commit()
    
    def query_all_missions(self):
        return self.session.query(Mission).all()
        
    def to_csv(self,path ):
        outfile = open(path, 'w')
        outcsv = csv.writer(outfile)
        records = self.query_all_missions()
        outcsv.writerow([column.name for column in Mission.__mapper__.columns])
        [outcsv.writerow([getattr(curr, column.name) for column in Mission.__mapper__.columns]) for curr in records]
        # or maybe use outcsv.writerows(records)

        outfile.close()

    def drop_all(self):
        self.base_class.metadata.drop_all(self.engine)

if __name__ == "__main__":
    MYSQL_USER = "example_user"
    MYSQL_DATABASE = "example_database"
    MYSQL_PASSWORD = "example_password"
    sql_port = 3306
    sql_endpoint = SQLEndpoint(url=f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@127.0.0.1:{sql_port}/{MYSQL_DATABASE}",base_class=Base)
    sql_endpoint.drop_all()
    sql_endpoint.init_data_base()
    klm_campain = Campaign(name="klm", description= "je suis klm")
    mission = Mission(packet_size=128,packet_send_frequency=1,energy_consume=12,packet_delivery_ratio=1.0,mission_time=500,e_drx_value=20.24,network_coordination_mode="Activate",radio_access_technologies_mode="NB-IoT",throughput=15)
    sql_endpoint.add_mission(mission=mission,campaign=klm_campain)
    print(sql_endpoint.query_all_missions())
    sql_endpoint.to_csv("klm.csv")