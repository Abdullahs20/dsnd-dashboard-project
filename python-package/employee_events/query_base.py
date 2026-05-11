# Import any dependencies needed to execute sql queries
from .sql_execution import QueryMixin


class QueryBase(QueryMixin):

    name = ''


    def names(self):

        return []



    def event_counts(self , id):


        return self.pandas_query(f"""
            select sum(positive_events) positive_events,
                   sum(negative_events) negative_events,
                   event_date
            from {self.name}
            join employee_events
            using({self.name}_id)
            WHERE {self.name}.{self.name}_id = {id}
            group by event_date
            order by event_date
        """)
            
    


    def notes(self ,id):


        return self.pandas_query(f"""
            select note_date, note
            from {self.name}
            join notes using ({self.name}_id)
            where {self.name}.{self.name}_id = {id}
            order by note_date
        """)


