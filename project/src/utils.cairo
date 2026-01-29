/// Utility Functions
/// 
/// Helper functions for the Monero light client.
/// All cryptographic operations use audited libraries.

use core::array::Span;
use core::poseidon::poseidon_hash_span;

/// Hashes an array of felt252 values using Poseidon
/// 
/// # Arguments
/// * `data` - The data to hash
///
/// # Returns
/// * `felt252` - The hash result
pub fn hash_data(data: Span<felt252>) -> felt252 {
    poseidon_hash_span(data)
}

/// TODO: Agent will add more utility functions as needed
