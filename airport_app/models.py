# models.py

from django.db import models
from django.core.exceptions import ValidationError


class AirportRoute(models.Model):
    # Each node can have left and right children.
    POSITION_CHOICES = (
        ('ROOT', 'Root'),
        ('L', 'Left'),
        ('R', 'Right'),
    )

    airport_code = models.CharField(
        max_length=10,
        help_text="Airport code (e.g., DXB, JFK, ABC)"
    )
    
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        help_text="Parent airport node"
    )
    
    position = models.CharField(
        max_length=5,
        choices=POSITION_CHOICES,
        help_text="Position relative to parent"
    )
    
    duration = models.IntegerField(
        default=0,
        help_text="Duration/Distance in km"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "Airport Route"
        verbose_name_plural = "Airport Routes"

    def __str__(self):
        return f"{self.airport_code} ({self.get_position_display()}) - {self.duration}km"

    def clean(self):
        """Validate the node before saving"""
        super().clean()
        
        # Root node validation
        if self.parent is None and self.position != 'ROOT':
            raise ValidationError("Root node must have position 'ROOT'")
        
        # Non-root node validation
        if self.parent is not None and self.position == 'ROOT':
            raise ValidationError("Only the root node can have position 'ROOT'")
        
        # Check for duplicate position under same parent
        if self.parent and self.position in ['L', 'R']:
            duplicate = AirportRoute.objects.filter(
                parent=self.parent, 
                position=self.position
            ).exclude(pk=self.pk)
            
            if duplicate.exists():
                raise ValidationError(
                    f"A {self.get_position_display()} child already exists for this parent."
                )

    def get_left_child(self):
        """Get the left child of this node"""
        return self.children.filter(position='L').first()

    def get_right_child(self):
        """Get the right child of this node"""
        return self.children.filter(position='R').first()

    def get_child(self, direction):
        """Get child based on direction"""
        if direction.lower() == 'left':
            return self.get_left_child()
        elif direction.lower() == 'right':
            return self.get_right_child()
        return None

    def find_last_reachable(self, direction):
        """
        Traverse continuously in the given direction until no more children exist.
        Returns the last reachable node.
        """
        current = self
        
        while True:
            child = current.get_child(direction)
            if child is None:
                return current
            current = child

    @staticmethod
    def get_all_nodes():
        """Get all nodes in the tree"""
        return AirportRoute.objects.all()

    @staticmethod
    def get_longest_duration_node():
        """Find the airport with the longest/maximum duration"""
        return AirportRoute.objects.order_by('-duration').first()

    @staticmethod
    def get_shortest_duration_node():
        """Find the airport with the shortest/minimum duration across entire route"""
        return AirportRoute.objects.order_by('duration').first()

    def get_tree_level(self):
        """Calculate the level/depth of this node in the tree"""
        level = 0
        current = self
        while current.parent:
            level += 1
            current = current.parent
        return level