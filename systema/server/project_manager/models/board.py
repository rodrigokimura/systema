from sqlmodel import Field, Session

from systema.base import BaseModel


class Board(BaseModel, table=True):
    id: str = Field(..., foreign_key="project.id", primary_key=True)

    def create_default_bins(self, session: Session):
        from systema.server.project_manager.models.bin import Bin

        todo = Bin(board_id=self.id, name="TO DO", order=0)
        in_progress = Bin(board_id=self.id, name="IN PROGRESS", order=1)
        done = Bin(board_id=self.id, name="DONE", order=2)
        session.add_all((todo, in_progress, done))
        session.commit()
