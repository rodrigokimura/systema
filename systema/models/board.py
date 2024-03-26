from sqlmodel import Session

from systema.models.project import SubProjectMixin


class Board(SubProjectMixin, table=True):
    def create_default_bins(self, session: Session):
        from systema.models.bin import Bin

        todo = Bin(board_id=self.id, name="TO DO", order=0)
        in_progress = Bin(board_id=self.id, name="IN PROGRESS", order=1)
        done = Bin(board_id=self.id, name="DONE", order=2)
        session.add_all((todo, in_progress, done))
        session.commit()
