class Point:
    def __init__(self,x=0,y=0):
        self.Update(x,y)
    def Update(self,x=None,y=None):
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
    def __str__(self):
        return f"({self.x},{self.y})"

class Polygon:
    def __init__(self,points):
        self.SetPoints(points)
    def SetPoints(self,points):
        if isinstance(points, Point):
            self.points = (points,)
        elif isinstance(points,list):
            self.points = tuple(points)
        elif isinstance(points, tuple):
            self.points = points

    def DoesPointIntersect(self,point=None,x=None,y=None):
        if not self.points:
            return None

        if x is None or y is None:
            if point is None:
                return None
            x, y = point.x, point.y

        num_vertices = len(self.points)
        inside = False

        # Store the first point in the polygon and initialize the second point
        p1 = self.points[0]

        # Loop through each edge in the polygon
        for i in range(1, num_vertices + 1):
            # Get the next point in the polygon
            p2 = self.points[i % num_vertices]

            # Check if the point is above the minimum y coordinate of the edge
            if y > min(p1.y, p2.y):
                # Check if the point is below the maximum y coordinate of the edge
                if y <= max(p1.y, p2.y):
                    # Check if the point is to the left of the maximum x coordinate of the edge
                    if x <= max(p1.x, p2.x):
                        # Calculate the x-intersection of the line connecting the point to the edge
                        x_intersection = (y - p1.y) * (p2.x - p1.x) / (p2.y - p1.y) + p1.x

                        # Check if the point is on the same line as the edge or to the left of the x-intersection
                        if p1.x == p2.x or x <= x_intersection:
                            # Flip the inside flag
                            inside = not inside

            # Store the current point as the first point for the next iteration
            p1 = p2

        # Return the value of the inside flag
        return inside
    def __str__(self):
        return " -> ".join([str(x) for x in self.points])

if __name__ == "__main__":
    polygon = Polygon([Point(10,10),Point(10,100),Point(100,100),Point(100,10)])
    point = Point(50,200)
    print(polygon.DoesPointIntersect(point))
