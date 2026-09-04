from rest_framework import serializers
from .models import Review, ReviewTargetType
from apps.rentals.models import Rental, RentalStatus
from apps.trust.services.scoring import TrustScoreEngine
from apps.trust.models import TrustEventType


class ReviewSerializer(serializers.ModelSerializer):
    reviewer_email = serializers.ReadOnlyField(source='reviewer.email')
    reviewee_email = serializers.ReadOnlyField(source='reviewee.email')
    asset_name = serializers.ReadOnlyField(source='asset.name')
    target_type_display = serializers.CharField(source='get_target_type_display', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'rental', 'reviewer', 'reviewer_email', 'reviewee',
            'reviewee_email', 'asset', 'asset_name', 'target_type',
            'target_type_display', 'rating', 'comment', 'created_at'
        ]
        read_only_fields = ['id', 'reviewer', 'reviewee', 'asset', 'created_at']


class ReviewCreateSerializer(serializers.ModelSerializer):
    rental_id = serializers.PrimaryKeyRelatedField(queryset=Rental.objects.all(), source='rental')

    class Meta:
        model = Review
        fields = ['rental_id', 'target_type', 'rating', 'comment']

    def validate(self, attrs):
        user = self.context['request'].user
        rental = attrs['rental']
        target_type = attrs['target_type']

        # Rule from Architecture Section 27: Reviews only available after completed rental
        if rental.status != RentalStatus.COMPLETED:
            raise serializers.ValidationError({"rental": "Reviews can only be submitted after the rental is COMPLETED."})

        # Validate participants
        if target_type in [ReviewTargetType.OWNER, ReviewTargetType.ASSET, ReviewTargetType.DRIVER]:
            if rental.renter != user:
                raise serializers.ValidationError("Only the renter can review the owner, asset, or driver.")
        elif target_type == ReviewTargetType.RENTER:
            if rental.owner != user:
                raise serializers.ValidationError("Only the owner can review the renter.")

        # Check unique constraint
        if Review.objects.filter(rental=rental, reviewer=user, target_type=target_type).exists():
            raise serializers.ValidationError("You have already submitted a review for this transaction.")

        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        rental = validated_data['rental']
        target_type = validated_data['target_type']
        rating = validated_data['rating']

        reviewee = None
        asset = None

        if target_type == ReviewTargetType.OWNER:
            reviewee = rental.owner
        elif target_type == ReviewTargetType.RENTER:
            reviewee = rental.renter
        elif target_type == ReviewTargetType.ASSET:
            asset = rental.listing.asset
        elif target_type == ReviewTargetType.DRIVER:
            if hasattr(rental, 'delivery_order') and rental.delivery_order.assigned_driver:
                reviewee = rental.delivery_order.assigned_driver

        review = Review.objects.create(
            rental=rental,
            reviewer=user,
            reviewee=reviewee,
            asset=asset,
            target_type=target_type,
            rating=rating,
            comment=validated_data.get('comment', '')
        )

        # Trigger Trust Score impact if person was reviewed
        if reviewee:
            if rating >= 4:
                TrustScoreEngine.record_event(
                    user=reviewee,
                    event_type=TrustEventType.POSITIVE_REVIEW,
                    reference_id=f"REV-{review.id}",
                    description=f"Received {rating}-star review on Rental #{rental.id}"
                )
            elif rating <= 2:
                TrustScoreEngine.record_event(
                    user=reviewee,
                    event_type=TrustEventType.NEGATIVE_REVIEW,
                    reference_id=f"REV-{review.id}",
                    description=f"Received {rating}-star review on Rental #{rental.id}"
                )

        return review
