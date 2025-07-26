import React from 'react';

const ProductCard = ({ product }) => {
  const handleAddToCart = () => {
    // In a real implementation, this would add to cart
    alert(`Would add ${product.name} to cart`);
  };

  return (
    <div className="product-card">
      {product.image_url && (
        <img 
          src={product.image_url} 
          alt={product.name}
          className="product-image"
        />
      )}
      <div className="product-details">
        <h3>{product.name}</h3>
        <p className="part-number">Part #: {product.part_number}</p>
        <p className="description">{product.description}</p>
        <div className="product-meta">
          <span className="price">${product.price}</span>
          <span className={`stock-status ${product.in_stock ? 'in-stock' : 'out-of-stock'}`}>
            {product.in_stock ? '✓ In Stock' : 'Out of Stock'}
          </span>
        </div>
        <div className="product-actions">
          <button 
            className="add-to-cart-btn"
            onClick={handleAddToCart}
            disabled={!product.in_stock}
          >
            Add to Cart
          </button>
          <button className="view-details-btn">
            View Details
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;