"""
Synapse Quantum Marketplace
The AWS Marketplace equivalent for quantum computing - discover, purchase, and deploy quantum algorithms and services
"""

import asyncio
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any


class MarketplaceCategory(str, Enum):
    """Quantum marketplace categories"""
    ALGORITHMS = "algorithms"
    DATASETS = "datasets"
    TOOLS = "tools"
    TEMPLATES = "templates"
    LIBRARIES = "libraries"
    SERVICES = "services"
    EDUCATION = "education"

class LicenseType(str, Enum):
    """Software licensing types"""
    FREE = "free"
    OPEN_SOURCE = "open_source"
    COMMERCIAL = "commercial"
    ENTERPRISE = "enterprise"
    ACADEMIC = "academic"
    TRIAL = "trial"

class PricingModel(str, Enum):
    """Pricing models for marketplace items"""
    FREE = "free"
    ONE_TIME = "one_time"
    SUBSCRIPTION = "subscription"
    PAY_PER_USE = "pay_per_use"
    FREEMIUM = "freemium"
    ENTERPRISE_QUOTE = "enterprise_quote"

class QuantumComplexity(str, Enum):
    """Quantum algorithm complexity levels"""
    BEGINNER = "beginner"      # 1-5 qubits
    INTERMEDIATE = "intermediate" # 6-20 qubits
    ADVANCED = "advanced"      # 21-50 qubits
    EXPERT = "expert"          # 50+ qubits
    RESEARCH = "research"      # Cutting-edge

@dataclass
class MarketplaceItem:
    """Base marketplace item"""
    item_id: str
    name: str
    description: str
    category: MarketplaceCategory
    version: str
    author: str
    author_email: str
    organization: str | None

    # Pricing
    pricing_model: PricingModel
    price: Decimal
    currency: str = "USD"

    # Licensing
    license_type: LicenseType
    license_text: str | None = None

    # Metadata
    tags: list[str]
    keywords: list[str]
    quantum_complexity: QuantumComplexity
    min_qubits: int
    max_qubits: int | None
    supported_backends: list[str]

    # Metrics
    downloads: int = 0
    rating: float = 0.0
    review_count: int = 0
    last_updated: datetime
    created_at: datetime

    # Content
    readme: str
    documentation_url: str | None = None
    source_code_url: str | None = None
    demo_url: str | None = None

    # Requirements
    dependencies: list[str] = None
    system_requirements: dict[str, Any] = None

    # Verification
    verified_by_synapse: bool = False
    security_scanned: bool = False
    performance_tested: bool = False

@dataclass
class QuantumAlgorithm(MarketplaceItem):
    """Quantum algorithm marketplace item"""
    algorithm_type: str  # "optimization", "search", "simulation", "ml", etc.
    time_complexity: str  # Big O notation
    space_complexity: str
    quantum_advantage: str  # Description of quantum speedup
    classical_equivalent: str | None = None

    # Performance metrics
    success_probability: float = 1.0
    error_rate: float = 0.0
    gate_count_estimate: int | None = None
    depth_estimate: int | None = None

@dataclass
class QuantumDataset(MarketplaceItem):
    """Quantum dataset marketplace item"""
    dataset_type: str  # "quantum_states", "measurement_data", "benchmark", etc.
    size_mb: float
    format: str  # "qasm", "json", "csv", "hdf5", etc.
    samples_count: int

    # Data characteristics
    quantum_states_included: bool = False
    measurement_data_included: bool = False
    classical_data_included: bool = False
    noise_model_included: bool = False

@dataclass
class QuantumTool(MarketplaceItem):
    """Quantum development tool marketplace item"""
    tool_type: str  # "visualizer", "debugger", "optimizer", "simulator", etc.
    supported_platforms: list[str]  # "web", "desktop", "cli", "api"
    integration_apis: list[str]  # "rest", "graphql", "websocket", etc.

    # Tool capabilities
    real_time_monitoring: bool = False
    batch_processing: bool = False
    cloud_integration: bool = False
    offline_usage: bool = True

@dataclass
class MarketplaceReview:
    """User review for marketplace item"""
    review_id: str
    item_id: str
    user_id: str
    username: str
    rating: int  # 1-5 stars
    title: str
    review_text: str
    verified_purchase: bool
    helpful_votes: int = 0
    created_at: datetime
    updated_at: datetime | None = None

class QuantumMarketplace:
    """Main quantum marketplace service"""

    def __init__(self):
        self.items = {}  # item_id -> MarketplaceItem
        self.reviews = {}  # item_id -> List[MarketplaceReview]
        self.user_purchases = {}  # user_id -> List[item_id]
        self.featured_items = []
        self.trending_items = []

        # Initialize with sample items
        self._initialize_sample_items()

    def _initialize_sample_items(self):
        """Initialize marketplace with sample quantum algorithms and tools"""

        # Grover's Search Algorithm
        grovers = QuantumAlgorithm(
            item_id="grover-search-v1",
            name="Grover's Search Algorithm",
            description="Quantum search algorithm providing quadratic speedup over classical search",
            category=MarketplaceCategory.ALGORITHMS,
            version="1.2.0",
            author="IBM Quantum",
            author_email="quantum@ibm.com",
            organization="IBM",
            pricing_model=PricingModel.PAY_PER_USE,
            price=Decimal("0.50"),
            license_type=LicenseType.COMMERCIAL,
            tags=["search", "optimization", "oracle"],
            keywords=["grover", "quantum search", "amplitude amplification"],
            quantum_complexity=QuantumComplexity.INTERMEDIATE,
            min_qubits=2,
            max_qubits=20,
            supported_backends=["ibm", "google", "aws"],
            downloads=15420,
            rating=4.8,
            review_count=89,
            last_updated=datetime(2024, 1, 15),
            created_at=datetime(2023, 6, 1),
            readme="# Grover's Algorithm\n\nQuantum search algorithm...",
            documentation_url="https://qiskit.org/textbook/ch-algorithms/grover.html",
            algorithm_type="search",
            time_complexity="O(√N)",
            space_complexity="O(log N)",
            quantum_advantage="Quadratic speedup over classical O(N) search",
            classical_equivalent="Linear search",
            success_probability=0.98,
            error_rate=0.02,
            gate_count_estimate=50,
            depth_estimate=20,
            verified_by_synapse=True,
            security_scanned=True,
            performance_tested=True
        )

        # Quantum Portfolio Optimization
        portfolio_opt = QuantumAlgorithm(
            item_id="quantum-portfolio-optimizer",
            name="Quantum Portfolio Optimizer",
            description="QAOA-based portfolio optimization for financial risk management",
            category=MarketplaceCategory.ALGORITHMS,
            version="2.0.1",
            author="Goldman Sachs Quantum",
            author_email="quantum@gs.com",
            organization="Goldman Sachs",
            pricing_model=PricingModel.PAY_PER_USE,
            price=Decimal("5.00"),
            license_type=LicenseType.COMMERCIAL,
            tags=["finance", "optimization", "risk", "portfolio"],
            keywords=["qaoa", "portfolio", "optimization", "risk management"],
            quantum_complexity=QuantumComplexity.ADVANCED,
            min_qubits=10,
            max_qubits=50,
            supported_backends=["ibm", "google", "aws", "quantinuum"],
            downloads=2340,
            rating=4.6,
            review_count=23,
            last_updated=datetime(2024, 1, 10),
            created_at=datetime(2023, 9, 15),
            readme="# Quantum Portfolio Optimization\n\nAdvanced portfolio optimization...",
            algorithm_type="optimization",
            time_complexity="O(2^n)",
            space_complexity="O(n²)",
            quantum_advantage="Explores solution space more efficiently than classical methods",
            classical_equivalent="Markowitz optimization",
            success_probability=0.85,
            error_rate=0.15,
            verified_by_synapse=True,
            security_scanned=True,
            performance_tested=True
        )

        # Molecular Docking Suite
        molecular_docking = QuantumAlgorithm(
            item_id="quantum-molecular-docking",
            name="Quantum Molecular Docking Suite",
            description="VQE-based molecular docking for drug discovery applications",
            category=MarketplaceCategory.ALGORITHMS,
            version="1.5.2",
            author="Roche Quantum Computing",
            author_email="quantum@roche.com",
            organization="Roche",
            pricing_model=PricingModel.PAY_PER_USE,
            price=Decimal("25.00"),
            license_type=LicenseType.COMMERCIAL,
            tags=["chemistry", "drug-discovery", "vqe", "molecules"],
            keywords=["molecular docking", "drug discovery", "vqe", "chemistry"],
            quantum_complexity=QuantumComplexity.EXPERT,
            min_qubits=20,
            max_qubits=100,
            supported_backends=["ibm", "google", "quantinuum"],
            downloads=890,
            rating=4.9,
            review_count=12,
            last_updated=datetime(2024, 1, 8),
            created_at=datetime(2023, 11, 1),
            readme="# Quantum Molecular Docking\n\nAdvanced molecular simulation...",
            algorithm_type="simulation",
            time_complexity="O(N⁴)",
            space_complexity="O(N²)",
            quantum_advantage="Exponential scaling advantage for molecular systems",
            classical_equivalent="Classical molecular dynamics",
            success_probability=0.92,
            error_rate=0.08,
            verified_by_synapse=True,
            security_scanned=True,
            performance_tested=True
        )

        # Quantum Chemistry Benchmark Dataset
        chem_dataset = QuantumDataset(
            item_id="quantum-chemistry-benchmark",
            name="Quantum Chemistry Benchmark Dataset",
            description="Comprehensive benchmark dataset for quantum chemistry algorithms",
            category=MarketplaceCategory.DATASETS,
            version="3.1.0",
            author="MIT Quantum Computing Lab",
            author_email="quantum@mit.edu",
            organization="MIT",
            pricing_model=PricingModel.SUBSCRIPTION,
            price=Decimal("100.00"),
            license_type=LicenseType.ACADEMIC,
            tags=["chemistry", "benchmark", "molecules", "vqe"],
            keywords=["quantum chemistry", "molecular", "benchmark", "dataset"],
            quantum_complexity=QuantumComplexity.ADVANCED,
            min_qubits=4,
            max_qubits=50,
            supported_backends=["any"],
            downloads=5670,
            rating=4.7,
            review_count=45,
            last_updated=datetime(2024, 1, 12),
            created_at=datetime(2023, 3, 20),
            readme="# Quantum Chemistry Benchmark\n\nComprehensive dataset...",
            dataset_type="quantum_states",
            size_mb=2500.0,
            format="hdf5",
            samples_count=50000,
            quantum_states_included=True,
            measurement_data_included=True,
            classical_data_included=True,
            noise_model_included=False,
            verified_by_synapse=True,
            security_scanned=True
        )

        # Quantum Circuit Visualizer Pro
        visualizer = QuantumTool(
            item_id="quantum-circuit-visualizer-pro",
            name="Quantum Circuit Visualizer Pro",
            description="Advanced quantum circuit visualization and analysis tool",
            category=MarketplaceCategory.TOOLS,
            version="2.3.1",
            author="Synapse Technologies",
            author_email="tools@synapse-lang.org",
            organization="Synapse",
            pricing_model=PricingModel.SUBSCRIPTION,
            price=Decimal("20.00"),
            license_type=LicenseType.COMMERCIAL,
            tags=["visualization", "analysis", "debugging", "circuit"],
            keywords=["circuit visualizer", "quantum debugging", "analysis"],
            quantum_complexity=QuantumComplexity.BEGINNER,
            min_qubits=1,
            max_qubits=1000,
            supported_backends=["any"],
            downloads=12450,
            rating=4.5,
            review_count=156,
            last_updated=datetime(2024, 1, 5),
            created_at=datetime(2023, 1, 10),
            readme="# Quantum Circuit Visualizer Pro\n\nAdvanced visualization...",
            tool_type="visualizer",
            supported_platforms=["web", "desktop"],
            integration_apis=["rest", "websocket"],
            real_time_monitoring=True,
            batch_processing=True,
            cloud_integration=True,
            offline_usage=True,
            verified_by_synapse=True,
            security_scanned=True
        )

        # Store items
        for item in [grovers, portfolio_opt, molecular_docking, chem_dataset, visualizer]:
            self.items[item.item_id] = item

        # Set featured and trending
        self.featured_items = [grovers.item_id, portfolio_opt.item_id, visualizer.item_id]
        self.trending_items = [molecular_docking.item_id, chem_dataset.item_id]

    async def search_marketplace(self,
                               query: str | None = None,
                               category: MarketplaceCategory | None = None,
                               tags: list[str] = None,
                               min_qubits: int | None = None,
                               max_qubits: int | None = None,
                               complexity: QuantumComplexity | None = None,
                               pricing_model: PricingModel | None = None,
                               license_type: LicenseType | None = None,
                               min_rating: float | None = None,
                               sort_by: str = "relevance",
                               limit: int = 20,
                               offset: int = 0) -> dict[str, Any]:
        """Search marketplace items with advanced filtering"""

        results = list(self.items.values())

        # Apply filters
        if query:
            query_lower = query.lower()
            results = [
                item for item in results
                if query_lower in item.name.lower() or
                   query_lower in item.description.lower() or
                   any(query_lower in tag.lower() for tag in item.tags) or
                   any(query_lower in keyword.lower() for keyword in item.keywords)
            ]

        if category:
            results = [item for item in results if item.category == category]

        if tags:
            results = [
                item for item in results
                if any(tag.lower() in [t.lower() for t in item.tags] for tag in tags)
            ]

        if min_qubits is not None:
            results = [item for item in results if item.min_qubits >= min_qubits]

        if max_qubits is not None:
            results = [item for item in results if
                      item.max_qubits is None or item.max_qubits <= max_qubits]

        if complexity:
            results = [item for item in results if item.quantum_complexity == complexity]

        if pricing_model:
            results = [item for item in results if item.pricing_model == pricing_model]

        if license_type:
            results = [item for item in results if item.license_type == license_type]

        if min_rating is not None:
            results = [item for item in results if item.rating >= min_rating]

        # Sort results
        if sort_by == "relevance":
            # For relevance, prioritize exact matches and popular items
            def relevance_score(item):
                score = 0
                if query:
                    if query.lower() in item.name.lower():
                        score += 10
                    if query.lower() in item.description.lower():
                        score += 5
                score += item.rating * 2
                score += min(item.downloads / 1000, 10)
                return score
            results.sort(key=relevance_score, reverse=True)
        elif sort_by == "popularity":
            results.sort(key=lambda x: x.downloads, reverse=True)
        elif sort_by == "rating":
            results.sort(key=lambda x: x.rating, reverse=True)
        elif sort_by == "newest":
            results.sort(key=lambda x: x.created_at, reverse=True)
        elif sort_by == "updated":
            results.sort(key=lambda x: x.last_updated, reverse=True)
        elif sort_by == "price_low":
            results.sort(key=lambda x: x.price)
        elif sort_by == "price_high":
            results.sort(key=lambda x: x.price, reverse=True)

        # Pagination
        total_count = len(results)
        paginated_results = results[offset:offset + limit]

        # Convert to serializable format
        items_data = []
        for item in paginated_results:
            item_dict = asdict(item)
            item_dict["price"] = float(item.price)
            item_dict["created_at"] = item.created_at.isoformat()
            item_dict["last_updated"] = item.last_updated.isoformat()
            items_data.append(item_dict)

        return {
            "items": items_data,
            "total_count": total_count,
            "page": (offset // limit) + 1,
            "total_pages": (total_count + limit - 1) // limit,
            "has_next": offset + limit < total_count,
            "has_previous": offset > 0
        }

    async def get_item_details(self, item_id: str) -> dict[str, Any]:
        """Get detailed information about a marketplace item"""

        if item_id not in self.items:
            raise ValueError(f"Item {item_id} not found")

        item = self.items[item_id]

        # Get reviews
        reviews = self.reviews.get(item_id, [])

        # Convert to serializable format
        item_dict = asdict(item)
        item_dict["price"] = float(item.price)
        item_dict["created_at"] = item.created_at.isoformat()
        item_dict["last_updated"] = item.last_updated.isoformat()

        # Add review data
        item_dict["reviews"] = [
            {
                "review_id": review.review_id,
                "username": review.username,
                "rating": review.rating,
                "title": review.title,
                "review_text": review.review_text,
                "verified_purchase": review.verified_purchase,
                "helpful_votes": review.helpful_votes,
                "created_at": review.created_at.isoformat()
            }
            for review in reviews[:10]  # Top 10 reviews
        ]

        # Add related items
        related_items = await self._get_related_items(item)
        item_dict["related_items"] = related_items

        return item_dict

    async def _get_related_items(self, item: MarketplaceItem, limit: int = 5) -> list[dict[str, Any]]:
        """Get related items based on tags and category"""

        candidates = []
        for candidate_id, candidate in self.items.items():
            if candidate_id == item.item_id:
                continue

            # Calculate similarity score
            score = 0

            # Same category
            if candidate.category == item.category:
                score += 3

            # Shared tags
            shared_tags = set(candidate.tags) & set(item.tags)
            score += len(shared_tags) * 2

            # Similar qubit requirements
            if abs(candidate.min_qubits - item.min_qubits) <= 5:
                score += 1

            # Same complexity level
            if candidate.quantum_complexity == item.quantum_complexity:
                score += 1

            candidates.append((candidate, score))

        # Sort by score and take top items
        candidates.sort(key=lambda x: x[1], reverse=True)
        top_candidates = candidates[:limit]

        related = []
        for candidate, score in top_candidates:
            related.append({
                "item_id": candidate.item_id,
                "name": candidate.name,
                "description": candidate.description[:100] + "...",
                "rating": candidate.rating,
                "price": float(candidate.price),
                "pricing_model": candidate.pricing_model.value
            })

        return related

    async def purchase_item(self, item_id: str, user_id: str) -> dict[str, Any]:
        """Purchase a marketplace item"""

        if item_id not in self.items:
            raise ValueError(f"Item {item_id} not found")

        item = self.items[item_id]

        # Check if already purchased
        user_purchases = self.user_purchases.get(user_id, [])
        if item_id in user_purchases:
            return {
                "status": "already_owned",
                "message": "You already own this item",
                "access_url": f"/marketplace/my-items/{item_id}"
            }

        # Process payment (simplified)
        if item.pricing_model == PricingModel.FREE:
            cost = Decimal("0.00")
        else:
            cost = item.price

        # Record purchase
        if user_id not in self.user_purchases:
            self.user_purchases[user_id] = []
        self.user_purchases[user_id].append(item_id)

        # Update download count
        item.downloads += 1

        purchase_id = f"purchase-{uuid.uuid4().hex[:12]}"

        return {
            "status": "success",
            "purchase_id": purchase_id,
            "item_id": item_id,
            "item_name": item.name,
            "cost": float(cost),
            "currency": item.currency,
            "access_url": f"/marketplace/my-items/{item_id}",
            "download_url": f"/marketplace/download/{item_id}",
            "purchased_at": datetime.utcnow().isoformat()
        }

    async def get_featured_items(self) -> list[dict[str, Any]]:
        """Get featured marketplace items"""

        featured = []
        for item_id in self.featured_items:
            if item_id in self.items:
                item = self.items[item_id]
                featured.append({
                    "item_id": item.item_id,
                    "name": item.name,
                    "description": item.description,
                    "category": item.category.value,
                    "rating": item.rating,
                    "downloads": item.downloads,
                    "price": float(item.price),
                    "pricing_model": item.pricing_model.value
                })

        return featured

    async def get_trending_items(self) -> list[dict[str, Any]]:
        """Get trending marketplace items"""

        trending = []
        for item_id in self.trending_items:
            if item_id in self.items:
                item = self.items[item_id]
                trending.append({
                    "item_id": item.item_id,
                    "name": item.name,
                    "description": item.description,
                    "category": item.category.value,
                    "rating": item.rating,
                    "downloads": item.downloads,
                    "price": float(item.price),
                    "pricing_model": item.pricing_model.value
                })

        return trending

    async def add_review(self,
                        item_id: str,
                        user_id: str,
                        username: str,
                        rating: int,
                        title: str,
                        review_text: str) -> str:
        """Add a review for a marketplace item"""

        if item_id not in self.items:
            raise ValueError(f"Item {item_id} not found")

        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")

        # Check if user purchased the item
        user_purchases = self.user_purchases.get(user_id, [])
        verified_purchase = item_id in user_purchases

        review_id = f"review-{uuid.uuid4().hex[:12]}"

        review = MarketplaceReview(
            review_id=review_id,
            item_id=item_id,
            user_id=user_id,
            username=username,
            rating=rating,
            title=title,
            review_text=review_text,
            verified_purchase=verified_purchase,
            created_at=datetime.utcnow()
        )

        # Store review
        if item_id not in self.reviews:
            self.reviews[item_id] = []
        self.reviews[item_id].append(review)

        # Update item rating
        item = self.items[item_id]
        all_ratings = [r.rating for r in self.reviews[item_id]]
        item.rating = sum(all_ratings) / len(all_ratings)
        item.review_count = len(all_ratings)

        return review_id

    async def get_categories(self) -> list[dict[str, Any]]:
        """Get marketplace categories with item counts"""

        category_counts = {}
        for item in self.items.values():
            category = item.category
            if category not in category_counts:
                category_counts[category] = 0
            category_counts[category] += 1

        categories = []
        for category in MarketplaceCategory:
            count = category_counts.get(category, 0)
            categories.append({
                "category": category.value,
                "display_name": category.value.replace("_", " ").title(),
                "item_count": count
            })

        return categories

    async def get_user_purchases(self, user_id: str) -> list[dict[str, Any]]:
        """Get user's purchased items"""

        purchased_ids = self.user_purchases.get(user_id, [])

        purchases = []
        for item_id in purchased_ids:
            if item_id in self.items:
                item = self.items[item_id]
                purchases.append({
                    "item_id": item.item_id,
                    "name": item.name,
                    "category": item.category.value,
                    "version": item.version,
                    "download_url": f"/marketplace/download/{item_id}",
                    "documentation_url": item.documentation_url
                })

        return purchases

# Example usage
if __name__ == "__main__":
    async def main():
        marketplace = QuantumMarketplace()

        # Search for algorithms
        print("=== Searching for optimization algorithms ===")
        results = await marketplace.search_marketplace(
            query="optimization",
            category=MarketplaceCategory.ALGORITHMS,
            sort_by="rating"
        )

        for item in results["items"]:
            print(f"{item['name']}: {item['rating']}⭐ - ${item['price']}")

        # Get featured items
        print("\n=== Featured Items ===")
        featured = await marketplace.get_featured_items()
        for item in featured:
            print(f"{item['name']}: {item['downloads']} downloads")

        # Purchase an item
        print("\n=== Purchase Item ===")
        purchase = await marketplace.purchase_item(
            item_id="grover-search-v1",
            user_id="user123"
        )
        print(f"Purchase status: {purchase['status']}")

        # Add a review
        print("\n=== Add Review ===")
        review_id = await marketplace.add_review(
            item_id="grover-search-v1",
            user_id="user123",
            username="quantum_dev",
            rating=5,
            title="Excellent implementation!",
            review_text="Very well optimized Grover's algorithm. Easy to use and well documented."
        )
        print(f"Review added: {review_id}")

    asyncio.run(main())
